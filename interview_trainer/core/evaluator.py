"""
evaluator.py – Rubric-based answer evaluation using IBM Granite.

Evaluates user answers against the rubric dimensions:
clarity, correctness, depth, structure, communication.
Outputs a JSON-validated score object with strengths, gaps, and an improved answer.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from interview_trainer.config import RUBRIC_DIMENSIONS
from interview_trainer.core.granite_client import GraniteClient, get_granite_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    """Score for a single rubric dimension."""

    dimension: str
    score: int          # 0-10
    feedback: str


@dataclass
class EvaluationResult:
    """Full evaluation result for a single answer."""

    question: str
    user_answer: str
    dimension_scores: list[DimensionScore]
    overall_score: float       # average of dimension scores
    strengths: list[str]
    gaps: list[str]
    improved_answer: str
    is_valid: bool = True       # False if the evaluation could not be parsed


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class AnswerEvaluator:
    """Evaluate interview answers using IBM Granite and a structured rubric.

    Args:
        client: :class:`GraniteClient` instance (uses singleton if not provided).
    """

    def __init__(self, client: Optional[GraniteClient] = None) -> None:
        self._client = client or get_granite_client()

    def evaluate(
        self,
        question: str,
        model_answer: str,
        user_answer: str,
        category: str = "technical",
    ) -> EvaluationResult:
        """Evaluate a user's answer against the rubric.

        Args:
            question:     The interview question that was asked.
            model_answer: The reference model answer.
            user_answer:  The candidate's submitted answer.
            category:     Question category for contextual rubric guidance.

        Returns:
            An :class:`EvaluationResult` with scores, feedback, and improvement.
        """
        if not user_answer.strip():
            return _empty_result(question, user_answer)

        prompt = _build_evaluation_prompt(
            question=question,
            model_answer=model_answer,
            user_answer=user_answer,
            category=category,
        )

        raw = self._client.generate_structured(prompt, max_new_tokens=1200)
        result = _parse_evaluation_json(raw, question, user_answer)
        return result


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _build_evaluation_prompt(
    question: str,
    model_answer: str,
    user_answer: str,
    category: str,
) -> str:
    star_hint = (
        "\nNote: this is a behavioral question. Evaluate the STAR structure "
        "(Situation, Task, Action, Result) as part of 'structure' dimension."
        if category == "behavioral"
        else ""
    )

    dimensions_desc = "\n".join(
        f"- {d.upper()}: {_dimension_description(d)}"
        for d in RUBRIC_DIMENSIONS
    )

    return f"""You are an expert interview coach evaluating a candidate's response.

QUESTION:
{question}

MODEL ANSWER (reference):
{model_answer}

CANDIDATE'S ANSWER:
{user_answer}
{star_hint}

RUBRIC DIMENSIONS (each scored 0-10):
{dimensions_desc}

INSTRUCTIONS:
1. Score each dimension from 0 (very poor) to 10 (excellent).
2. Identify 2-4 specific strengths in the answer.
3. Identify 2-4 specific gaps or areas for improvement.
4. Write an improved version of the answer that addresses the gaps.
5. Be constructive and specific — avoid vague praise or criticism.

Respond with this EXACT JSON structure (no extra text):
{{
  "scores": {{
    "clarity": <0-10>,
    "correctness": <0-10>,
    "depth": <0-10>,
    "structure": <0-10>,
    "communication": <0-10>
  }},
  "feedback": {{
    "clarity": "<specific feedback>",
    "correctness": "<specific feedback>",
    "depth": "<specific feedback>",
    "structure": "<specific feedback>",
    "communication": "<specific feedback>"
  }},
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<gap 1>", "<gap 2>", "<gap 3>"],
  "improved_answer": "<complete improved answer>"
}}"""


def _dimension_description(dimension: str) -> str:
    descriptions = {
        "clarity": "Is the answer clear, logical, and easy to follow?",
        "correctness": "Is the information technically accurate?",
        "depth": "Does the answer show sufficient depth and expertise?",
        "structure": "Is the answer well-organised with a clear flow?",
        "communication": "Is the language professional and confident?",
    }
    return descriptions.get(dimension, dimension)


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

def _parse_evaluation_json(
    raw: str, question: str, user_answer: str
) -> EvaluationResult:
    """Parse Granite's JSON evaluation output with validation and fallback."""
    raw = raw.strip()

    # Extract JSON object
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        logger.warning("No JSON object in evaluation response: %s", raw[:200])
        return _fallback_result(question, user_answer, raw)

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as exc:
        logger.warning("Evaluation JSON parse error: %s", exc)
        return _fallback_result(question, user_answer, raw)

    # Validate and extract scores
    scores_raw = data.get("scores", {})
    feedback_raw = data.get("feedback", {})

    dimension_scores: list[DimensionScore] = []
    for dim in RUBRIC_DIMENSIONS:
        raw_score = scores_raw.get(dim, 5)
        try:
            score = max(0, min(10, int(raw_score)))
        except (ValueError, TypeError):
            score = 5
        fb = str(feedback_raw.get(dim, "No specific feedback.")).strip()
        dimension_scores.append(DimensionScore(dimension=dim, score=score, feedback=fb))

    overall = sum(d.score for d in dimension_scores) / len(dimension_scores)

    strengths = _as_list(data.get("strengths", []))
    gaps = _as_list(data.get("gaps", []))
    improved = str(data.get("improved_answer", "")).strip()

    if not strengths:
        strengths = ["Answer shows some understanding of the topic."]
    if not gaps:
        gaps = ["Could benefit from more specific examples."]

    return EvaluationResult(
        question=question,
        user_answer=user_answer,
        dimension_scores=dimension_scores,
        overall_score=round(overall, 1),
        strengths=strengths,
        gaps=gaps,
        improved_answer=improved,
        is_valid=True,
    )


def _fallback_result(question: str, user_answer: str, raw: str) -> EvaluationResult:
    """Return a graceful fallback when parsing fails."""
    default_scores = [
        DimensionScore(dim, 5, "Evaluation could not be fully parsed.") 
        for dim in RUBRIC_DIMENSIONS
    ]
    return EvaluationResult(
        question=question,
        user_answer=user_answer,
        dimension_scores=default_scores,
        overall_score=5.0,
        strengths=["Answer was submitted for review."],
        gaps=["Automated evaluation encountered an issue. Please try again."],
        improved_answer=raw[:500] if raw else "",
        is_valid=False,
    )


def _empty_result(question: str, user_answer: str) -> EvaluationResult:
    """Return a result indicating no answer was provided."""
    default_scores = [DimensionScore(dim, 0, "No answer provided.") for dim in RUBRIC_DIMENSIONS]
    return EvaluationResult(
        question=question,
        user_answer=user_answer,
        dimension_scores=default_scores,
        overall_score=0.0,
        strengths=[],
        gaps=["No answer was provided."],
        improved_answer="",
        is_valid=False,
    )


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    if isinstance(value, str):
        return [value.strip()]
    return []
