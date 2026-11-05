"""
test_evaluator.py – Tests for the rubric-based answer evaluator.

Mocks the GraniteClient so no real API calls are made.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from interview_trainer.core.evaluator import (
    AnswerEvaluator,
    EvaluationResult,
    DimensionScore,
    _parse_evaluation_json,
    _empty_result,
    _fallback_result,
)
from interview_trainer.config import RUBRIC_DIMENSIONS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_EVAL_RESPONSE = json.dumps({
    "scores": {
        "clarity": 7,
        "correctness": 8,
        "depth": 6,
        "structure": 7,
        "communication": 8,
    },
    "feedback": {
        "clarity": "Answer is clear and well-organised.",
        "correctness": "Technically accurate.",
        "depth": "Could include more examples.",
        "structure": "Good logical flow.",
        "communication": "Professional tone.",
    },
    "strengths": ["Good use of examples", "Clear explanation"],
    "gaps": ["Lacks code snippet", "Missing edge cases"],
    "improved_answer": "An improved version of the answer…",
})

INVALID_JSON_RESPONSE = "Here is some prose without JSON."

PARTIAL_JSON_RESPONSE = '{"scores": {"clarity": 5}}'  # Missing dimensions


def _make_mock_client(response: str) -> MagicMock:
    client = MagicMock()
    client.generate_structured.return_value = response
    return client


# ---------------------------------------------------------------------------
# _parse_evaluation_json
# ---------------------------------------------------------------------------

class TestParseEvaluationJson:
    def test_valid_response_returns_result(self):
        result = _parse_evaluation_json(
            VALID_EVAL_RESPONSE, "What is OOP?", "My answer"
        )
        assert isinstance(result, EvaluationResult)
        assert result.is_valid is True
        assert result.overall_score > 0

    def test_all_dimensions_present(self):
        result = _parse_evaluation_json(
            VALID_EVAL_RESPONSE, "Q?", "A"
        )
        dims = {ds.dimension for ds in result.dimension_scores}
        assert dims == set(RUBRIC_DIMENSIONS)

    def test_scores_clamped_to_10(self):
        response = json.dumps({
            "scores": {d: 15 for d in RUBRIC_DIMENSIONS},
            "feedback": {d: "ok" for d in RUBRIC_DIMENSIONS},
            "strengths": [],
            "gaps": [],
            "improved_answer": "",
        })
        result = _parse_evaluation_json(response, "Q?", "A")
        for ds in result.dimension_scores:
            assert ds.score <= 10

    def test_invalid_json_returns_fallback(self):
        result = _parse_evaluation_json(INVALID_JSON_RESPONSE, "Q?", "A")
        assert isinstance(result, EvaluationResult)
        assert result.is_valid is False

    def test_overall_score_is_average(self):
        result = _parse_evaluation_json(VALID_EVAL_RESPONSE, "Q?", "A")
        expected_avg = (7 + 8 + 6 + 7 + 8) / 5
        assert result.overall_score == pytest.approx(expected_avg, abs=0.1)

    def test_strengths_extracted(self):
        result = _parse_evaluation_json(VALID_EVAL_RESPONSE, "Q?", "A")
        assert len(result.strengths) == 2
        assert "Good use of examples" in result.strengths

    def test_gaps_extracted(self):
        result = _parse_evaluation_json(VALID_EVAL_RESPONSE, "Q?", "A")
        assert len(result.gaps) == 2

    def test_improved_answer_extracted(self):
        result = _parse_evaluation_json(VALID_EVAL_RESPONSE, "Q?", "A")
        assert "improved" in result.improved_answer.lower()


# ---------------------------------------------------------------------------
# _empty_result
# ---------------------------------------------------------------------------

class TestEmptyResult:
    def test_empty_result_score_is_zero(self):
        result = _empty_result("Q?", "")
        assert result.overall_score == 0.0
        assert result.is_valid is False

    def test_empty_result_has_all_dimensions(self):
        result = _empty_result("Q?", "")
        dims = {ds.dimension for ds in result.dimension_scores}
        assert dims == set(RUBRIC_DIMENSIONS)


# ---------------------------------------------------------------------------
# AnswerEvaluator (mocked client)
# ---------------------------------------------------------------------------

class TestAnswerEvaluator:
    def test_evaluate_returns_result(self):
        client = _make_mock_client(VALID_EVAL_RESPONSE)
        evaluator = AnswerEvaluator(client=client)
        result = evaluator.evaluate(
            question="What is OOP?",
            model_answer="OOP has four pillars…",
            user_answer="OOP is a paradigm with encapsulation and inheritance.",
        )
        assert isinstance(result, EvaluationResult)
        assert result.is_valid is True
        client.generate_structured.assert_called_once()

    def test_empty_user_answer_returns_zero_score(self):
        client = _make_mock_client(VALID_EVAL_RESPONSE)
        evaluator = AnswerEvaluator(client=client)
        result = evaluator.evaluate(
            question="Q?",
            model_answer="Model answer",
            user_answer="   ",
        )
        assert result.overall_score == 0.0
        # Should NOT call the API for empty answers
        client.generate_structured.assert_not_called()

    def test_invalid_api_response_returns_fallback(self):
        client = _make_mock_client(INVALID_JSON_RESPONSE)
        evaluator = AnswerEvaluator(client=client)
        result = evaluator.evaluate(
            question="Q?",
            model_answer="Model",
            user_answer="Some answer",
        )
        assert result.is_valid is False
        assert result.overall_score == 5.0  # fallback default

    def test_partial_json_still_returns_result(self):
        client = _make_mock_client(PARTIAL_JSON_RESPONSE)
        evaluator = AnswerEvaluator(client=client)
        result = evaluator.evaluate(
            question="Q?",
            model_answer="Model",
            user_answer="Answer with partial feedback",
        )
        # Should not raise; returns result (valid or fallback)
        assert isinstance(result, EvaluationResult)
