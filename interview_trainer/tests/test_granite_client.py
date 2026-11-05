"""
test_granite_client.py – Tests for the GraniteClient wrapper.

Mocks the ibm-watsonx-ai SDK; no real API calls are made.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from interview_trainer.core.granite_client import (
    GraniteClient,
    GraniteAPIError,
    GraniteCredentialsError,
)


# ---------------------------------------------------------------------------
# Helper: build a client whose _call_model returns a fixed string
# ---------------------------------------------------------------------------

def _make_client(response: str = "Generated text") -> GraniteClient:
    """Return a GraniteClient that returns `response` from _call_model."""
    client = GraniteClient(api_key="sk-key", project_id="proj")
    # Patch at the instance level so no real SDK is needed
    client._call_model = MagicMock(return_value=response)  # type: ignore[method-assign]
    # Still need _client to exist so _validate_credentials passes
    client._client = MagicMock()
    return client


# ---------------------------------------------------------------------------
# Credential validation
# ---------------------------------------------------------------------------

class TestCredentialValidation:
    def test_missing_api_key_raises(self):
        with patch("interview_trainer.core.granite_client.WATSONX_API_KEY", ""), \
             patch("interview_trainer.core.granite_client.WATSONX_PROJECT_ID", "proj-123"):
            client = GraniteClient(api_key="", project_id="proj-123")
            with pytest.raises(GraniteCredentialsError, match="WATSONX_API_KEY"):
                client.generate("hello")

    def test_missing_project_id_raises(self):
        with patch("interview_trainer.core.granite_client.WATSONX_API_KEY", "sk-abc"), \
             patch("interview_trainer.core.granite_client.WATSONX_PROJECT_ID", ""):
            client = GraniteClient(api_key="sk-abc", project_id="")
            with pytest.raises(GraniteCredentialsError, match="WATSONX_PROJECT_ID"):
                client.generate("hello")

    def test_both_present_does_not_raise_on_credentials(self):
        """With valid credentials, error should come from _call_model, not credential check."""
        client = GraniteClient(api_key="sk-abc", project_id="proj-123")
        client._client = MagicMock()
        client._call_model = MagicMock(side_effect=Exception("connection error"))  # type: ignore[method-assign]
        with pytest.raises(GraniteAPIError):
            client.generate("hello")


# ---------------------------------------------------------------------------
# Successful generation
# ---------------------------------------------------------------------------

class TestGenerate:
    def test_returns_string(self):
        client = _make_client("Hello, World!")
        result = client.generate("Say hello")
        assert result == "Hello, World!"

    def test_strips_whitespace(self):
        client = _make_client("  trimmed  ")
        result = client.generate("test")
        assert result == "trimmed"

    def test_generate_called_with_prompt(self):
        client = _make_client("response")
        client.generate("test prompt")
        client._call_model.assert_called_once()
        call_args = str(client._call_model.call_args)
        assert "test prompt" in call_args


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------

class TestRetry:
    def test_retries_on_transient_error(self):
        """Client should retry up to LLM_MAX_RETRIES times."""
        client = GraniteClient(api_key="sk-key", project_id="proj")
        client._client = MagicMock()
        # Fail twice, succeed third
        client._call_model = MagicMock(side_effect=[  # type: ignore[method-assign]
            Exception("timeout"),
            Exception("timeout"),
            "Success!",
        ])
        with patch("interview_trainer.core.granite_client.time.sleep"):
            result = client.generate("prompt")
        assert result == "Success!"
        assert client._call_model.call_count == 3

    def test_raises_after_max_retries(self):
        client = GraniteClient(api_key="sk-key", project_id="proj")
        client._client = MagicMock()
        client._call_model = MagicMock(side_effect=Exception("persistent error"))  # type: ignore[method-assign]
        with patch("interview_trainer.core.granite_client.time.sleep"):
            with pytest.raises(GraniteAPIError, match="failed after"):
                client.generate("prompt")

    def test_auth_error_not_retried(self):
        client = GraniteClient(api_key="sk-key", project_id="proj")
        client._client = MagicMock()
        client._call_model = MagicMock(side_effect=Exception("401 Unauthorized"))  # type: ignore[method-assign]
        with patch("interview_trainer.core.granite_client.time.sleep"):
            with pytest.raises(GraniteCredentialsError):
                client.generate("prompt")
        # Should not retry auth errors
        assert client._call_model.call_count == 1


# ---------------------------------------------------------------------------
# Dict response extraction
# ---------------------------------------------------------------------------

class TestExtractTextFromDict:
    def test_extracts_from_results_path(self):
        d = {"results": [{"generated_text": "hello"}]}
        assert GraniteClient._extract_text_from_dict(d) == "hello"

    def test_extracts_from_flat_path(self):
        d = {"generated_text": "world"}
        assert GraniteClient._extract_text_from_dict(d) == "world"

    def test_falls_back_to_str(self):
        d = {"unknown": "value"}
        result = GraniteClient._extract_text_from_dict(d)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# generate_structured
# ---------------------------------------------------------------------------

class TestGenerateStructured:
    def test_appends_json_instruction(self):
        client = _make_client('{"key": "value"}')
        client.generate_structured("base prompt")
        # The prompt passed to _call_model should contain "JSON"
        called_prompt = str(client._call_model.call_args)
        assert "JSON" in called_prompt
