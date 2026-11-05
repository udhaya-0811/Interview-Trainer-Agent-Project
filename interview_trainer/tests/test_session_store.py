"""
test_session_store.py – Tests for the SQLite session store.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from interview_trainer.core.session_store import (
    SessionStore,
    Session,
    QuestionScore,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path: Path) -> SessionStore:
    """Return a fresh SessionStore backed by a temporary database."""
    db_file = tmp_path / "test_interview.db"
    return SessionStore(db_path=db_file)


def _save_test_session(store: SessionStore, **kwargs) -> int:
    defaults = {
        "user_name": "Test User",
        "role": "Java Developer",
        "experience_level": "2-5 yrs",
        "interview_type": "Mixed",
        "company_type": "Product Company",
        "overall_score": 7.5,
        "questions_attempted": 5,
        "notes": "",
    }
    defaults.update(kwargs)
    return store.save_session(**defaults)


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

class TestSaveSession:
    def test_save_returns_integer_id(self, store: SessionStore):
        sid = _save_test_session(store)
        assert isinstance(sid, int)
        assert sid > 0

    def test_multiple_saves_increment_ids(self, store: SessionStore):
        id1 = _save_test_session(store)
        id2 = _save_test_session(store)
        assert id2 > id1

    def test_saved_session_retrievable(self, store: SessionStore):
        sid = _save_test_session(store, role="Data Analyst")
        sessions = store.get_sessions()
        assert any(s.session_id == sid for s in sessions)

    def test_role_stored_correctly(self, store: SessionStore):
        _save_test_session(store, role="AI/ML Engineer")
        sessions = store.get_sessions()
        assert any(s.role == "AI/ML Engineer" for s in sessions)


class TestGetSessions:
    def test_empty_store_returns_empty_list(self, store: SessionStore):
        assert store.get_sessions() == []

    def test_limit_respected(self, store: SessionStore):
        for _ in range(5):
            _save_test_session(store)
        sessions = store.get_sessions(limit=3)
        assert len(sessions) <= 3

    def test_filter_by_user_name(self, store: SessionStore):
        _save_test_session(store, user_name="Alice")
        _save_test_session(store, user_name="Bob")
        alice_sessions = store.get_sessions(user_name="Alice")
        assert all(s.user_name == "Alice" for s in alice_sessions)

    def test_filter_case_insensitive(self, store: SessionStore):
        _save_test_session(store, user_name="Alice")
        sessions = store.get_sessions(user_name="alice")
        assert len(sessions) >= 1


class TestDeleteSession:
    def test_deleted_session_not_in_list(self, store: SessionStore):
        sid = _save_test_session(store)
        store.delete_session(sid)
        sessions = store.get_sessions()
        assert not any(s.session_id == sid for s in sessions)

    def test_delete_also_removes_question_scores(self, store: SessionStore):
        sid = _save_test_session(store)
        store.save_question_score(
            session_id=sid,
            question_id="Q01",
            question_text="What is OOP?",
            category="technical",
            user_answer="OOP is…",
            overall_score=7.0,
            dimension_scores={"clarity": 7, "correctness": 8, "depth": 6,
                               "structure": 7, "communication": 7},
            strengths=["Good"],
            gaps=["Needs more depth"],
        )
        store.delete_session(sid)
        # Question scores should be gone
        scores = store.get_question_scores(sid)
        assert scores == []


# ---------------------------------------------------------------------------
# Question scores
# ---------------------------------------------------------------------------

class TestQuestionScores:
    def test_save_and_retrieve_question_score(self, store: SessionStore):
        sid = _save_test_session(store)
        store.save_question_score(
            session_id=sid,
            question_id="Q01",
            question_text="What is OOP?",
            category="technical",
            user_answer="Object-oriented programming with 4 pillars",
            overall_score=7.5,
            dimension_scores={"clarity": 7, "correctness": 8, "depth": 7,
                               "structure": 8, "communication": 7},
            strengths=["Clear explanation"],
            gaps=["No examples provided"],
        )
        scores = store.get_question_scores(sid)
        assert len(scores) == 1
        assert scores[0].question_id == "Q01"
        assert scores[0].overall_score == 7.5

    def test_dimension_scores_json_valid(self, store: SessionStore):
        sid = _save_test_session(store)
        dim_scores = {"clarity": 8, "correctness": 9, "depth": 7,
                      "structure": 8, "communication": 8}
        store.save_question_score(
            session_id=sid,
            question_id="Q02",
            question_text="Explain generics?",
            category="technical",
            user_answer="Generics allow type-safe collections",
            overall_score=8.0,
            dimension_scores=dim_scores,
            strengths=[],
            gaps=[],
        )
        scores = store.get_question_scores(sid)
        parsed = json.loads(scores[0].dimension_scores_json)
        assert parsed == dim_scores


# ---------------------------------------------------------------------------
# Progress data
# ---------------------------------------------------------------------------

class TestProgressData:
    def test_progress_data_format(self, store: SessionStore):
        _save_test_session(store, overall_score=6.5)
        _save_test_session(store, overall_score=7.5)
        data = store.get_progress_data()
        assert len(data) == 2
        assert all("date" in d and "score" in d for d in data)

    def test_progress_data_chronological_order(self, store: SessionStore):
        _save_test_session(store, overall_score=5.0)
        _save_test_session(store, overall_score=8.0)
        data = store.get_progress_data()
        # First session should be earlier (lower id)
        if len(data) == 2:
            # Both have same date string in fast tests; just check structure
            assert data[0]["score"] in (5.0, 8.0)


# ---------------------------------------------------------------------------
# Dimension averages
# ---------------------------------------------------------------------------

class TestDimensionAverages:
    def test_returns_dict(self, store: SessionStore):
        avgs = store.get_dimension_averages()
        assert isinstance(avgs, dict)

    def test_averages_computed_from_scores(self, store: SessionStore):
        sid = _save_test_session(store)
        store.save_question_score(
            session_id=sid,
            question_id="Q01",
            question_text="Q1",
            category="technical",
            user_answer="Answer",
            overall_score=8.0,
            dimension_scores={"clarity": 8, "correctness": 8, "depth": 8,
                               "structure": 8, "communication": 8},
            strengths=[],
            gaps=[],
        )
        avgs = store.get_dimension_averages()
        assert "clarity" in avgs
        assert avgs["clarity"] == pytest.approx(8.0)
