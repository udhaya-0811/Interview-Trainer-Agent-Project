"""
granite_client.py – IBM watsonx.ai / Granite LLM wrapper.

All LLM calls go through this module. Credentials are read exclusively from
environment variables – never hardcoded.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

from interview_trainer.config import (
    LLM_MAX_NEW_TOKENS,
    LLM_MAX_RETRIES,
    LLM_REPETITION_PENALTY,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    LLM_TOP_P,
    WATSONX_API_KEY,
    WATSONX_MODEL_ID,
    WATSONX_PROJECT_ID,
    WATSONX_URL,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class GraniteClientError(Exception):
    """Raised when the Granite client encounters an unrecoverable error."""


class GraniteCredentialsError(GraniteClientError):
    """Raised when required IBM credentials are missing or invalid."""


class GraniteAPIError(GraniteClientError):
    """Raised when the watsonx.ai API returns an error response."""


# ---------------------------------------------------------------------------
# GraniteClient
# ---------------------------------------------------------------------------

class GraniteClient:
    """Thin wrapper around the ibm-watsonx-ai SDK for IBM Granite models.

    Handles authentication, retries with exponential back-off, and timeout.
    All generation parameters are configurable via :mod:`interview_trainer.config`.

    Usage::

        client = GraniteClient()
        response = client.generate("Explain recursion in Python.")
        print(response)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        project_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or WATSONX_API_KEY
        self._url = url or WATSONX_URL
        self._project_id = project_id or WATSONX_PROJECT_ID
        self._model_id = model_id or WATSONX_MODEL_ID
        self._client = None  # lazy init

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS,
        temperature: float = LLM_TEMPERATURE,
        stop_sequences: Optional[list[str]] = None,
    ) -> str:
        """Generate text from a prompt using IBM Granite on watsonx.ai.

        Args:
            prompt:          The full prompt string to send to the model.
            max_new_tokens:  Maximum tokens to generate.
            temperature:     Sampling temperature (lower = more deterministic).
            stop_sequences:  Optional list of stop strings.

        Returns:
            Generated text as a string.

        Raises:
            GraniteCredentialsError: If credentials are missing.
            GraniteAPIError:         If the API returns an error after all retries.
        """
        self._validate_credentials()
        client = self._get_client()

        params = self._build_params(max_new_tokens, temperature, stop_sequences)
        last_error: Optional[Exception] = None

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                logger.debug(
                    "Granite generate – attempt %d/%d, model=%s",
                    attempt, LLM_MAX_RETRIES, self._model_id,
                )
                # Use chat API (current) with fallback to generate_text (legacy)
                result = self._call_model(client, prompt, params)
                if isinstance(result, str):
                    return result.strip()
                if isinstance(result, dict):
                    return self._extract_text_from_dict(result)
                return str(result).strip()

            except Exception as exc:  # noqa: BLE001
                last_error = exc
                error_str = str(exc)
                # Do not retry on auth errors
                if "401" in error_str or "403" in error_str or "authentication" in error_str.lower():
                    raise GraniteCredentialsError(
                        f"Authentication failed. Check WATSONX_API_KEY and "
                        f"WATSONX_PROJECT_ID environment variables. Detail: {exc}"
                    ) from exc
                # Do not retry on unsupported model – surface a clear message
                if "not supported" in error_str.lower() or "supported models" in error_str.lower():
                    raise GraniteAPIError(
                        f"Model '{self._model_id}' is not available in your watsonx.ai project. "
                        f"Set WATSONX_MODEL_ID in your .env file to one of your project's supported models. "
                        f"Detail: {exc}"
                    ) from exc
                if attempt < LLM_MAX_RETRIES:
                    backoff = 2 ** attempt
                    logger.warning(
                        "Granite API error (attempt %d/%d), retrying in %ds: %s",
                        attempt, LLM_MAX_RETRIES, backoff, exc,
                    )
                    time.sleep(backoff)

        raise GraniteAPIError(
            f"Granite API failed after {LLM_MAX_RETRIES} attempts. "
            f"Last error: {last_error}"
        ) from last_error

    def generate_structured(
        self,
        prompt: str,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS,
    ) -> str:
        """Convenience wrapper that encourages JSON output.

        Works with both instruct and base Granite models.
        For base models the prompt is already formatted by the caller;
        we just append a JSON reminder and use greedy decoding for consistency.
        """
        json_instruction = (
            "\n\nIMPORTANT: Respond with valid JSON only. "
            "Do not include markdown fences, explanations, or any text outside the JSON."
        )
        return self.generate(
            prompt + json_instruction,
            max_new_tokens=max_new_tokens,
            temperature=0.0,   # greedy = most deterministic JSON output
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_credentials(self) -> None:
        missing = []
        if not self._api_key:
            missing.append("WATSONX_API_KEY")
        if not self._project_id:
            missing.append("WATSONX_PROJECT_ID")
        if missing:
            raise GraniteCredentialsError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Create a .env file (see .env.example) or set them in your environment."
            )

    def _call_model(self, client, prompt: str, params: dict) -> str:
        """Call the model using chat API (preferred) or generate_text (legacy fallback)."""
        # Try chat API first (current watsonx.ai SDK standard)
        try:
            response = client.chat(
                messages=[{"role": "user", "content": prompt}],
                params=params,
            )
            # Extract content from chat response
            if isinstance(response, dict):
                choices = response.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
            return str(response)
        except Exception:
            # Fallback to generate_text for models that don't support chat
            return client.generate_text(prompt=prompt, params=params)

    def _get_client(self):
        """Lazy-initialise the watsonx.ai ModelInference client."""
        if self._client is None:
            try:
                from ibm_watsonx_ai import Credentials  # type: ignore
                from ibm_watsonx_ai.foundation_models import ModelInference  # type: ignore
            except ImportError as exc:
                raise GraniteClientError(
                    "ibm-watsonx-ai is not installed. "
                    "Run: pip install ibm-watsonx-ai"
                ) from exc

            credentials = Credentials(
                api_key=self._api_key,
                url=self._url,
            )
            self._client = ModelInference(
                model_id=self._model_id,
                credentials=credentials,
                project_id=self._project_id,
            )
        return self._client

    def _build_params(
        self,
        max_new_tokens: int,
        temperature: float,
        stop_sequences: Optional[list[str]],
    ) -> Any:
        """Build GenTextParamsMetaNames params object."""
        try:
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams  # type: ignore

            use_greedy = temperature <= 0
            params: dict[str, Any] = {
                GenParams.DECODING_METHOD: "greedy" if use_greedy else "sample",
                GenParams.MAX_NEW_TOKENS: max_new_tokens,
                GenParams.REPETITION_PENALTY: LLM_REPETITION_PENALTY,
            }
            # temperature and top_p only apply to sample decoding
            if not use_greedy:
                params[GenParams.TEMPERATURE] = temperature
                params[GenParams.TOP_P] = LLM_TOP_P
            if stop_sequences:
                params[GenParams.STOP_SEQUENCES] = stop_sequences
            return params
        except ImportError:
            # Older SDK or different structure — pass plain dict
            use_greedy = temperature <= 0
            params = {
                "decoding_method": "greedy" if use_greedy else "sample",
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": LLM_REPETITION_PENALTY,
            }
            if not use_greedy:
                params["temperature"] = temperature
                params["top_p"] = LLM_TOP_P
            if stop_sequences:
                params["stop_sequences"] = stop_sequences
            return params

    @staticmethod
    def _extract_text_from_dict(result: dict) -> str:
        """Extract generated text from a dict response (older SDK versions)."""
        # Try common paths
        for path in [
            ["results", 0, "generated_text"],
            ["generated_text"],
            ["predictions", 0, "generated_text"],
        ]:
            try:
                obj = result
                for key in path:
                    obj = obj[key]  # type: ignore[index]
                return str(obj).strip()
            except (KeyError, IndexError, TypeError):
                continue
        return str(result)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_client_singleton: Optional[GraniteClient] = None


def get_granite_client() -> GraniteClient:
    """Return the module-level :class:`GraniteClient` singleton."""
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = GraniteClient()
    return _client_singleton
