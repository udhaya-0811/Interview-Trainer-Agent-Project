"""
session_store.py – SQLite-backed session history for Interview Trainer.

Stores session metadata and per-question scores for progress tracking.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional

from interview_trainer.config import DB_PATH

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Session:
    """One complete interview training session."""

    session_id: Optional[int]
    user_name: str
    role: str
    experience_level: str
    interview_type: str
    company_type: str
    created_at: str             # ISO 8601 timestamp
    overall_score: float        # average score across all evaluated answers
    questions_attempted: int
    notes: str = ""


@dataclass
class QuestionScore:
    """Per-question score record linked to a session."""

    score_id: Optional[int]
    session_id: int
    question_id: str
    question_text: str
    category: str
    user_answer: str
    overall_score: float
    dimension_scores_json: str   # JSON-encoded dict
    strengths_json: str          # JSON-encoded list
    gaps_json: str               # JSON-encoded list


# ---------------------------------------------------------------------------
# Session store
# ---------------------------------------------------------------------------

class SessionStore:
    """SQLite-backed store for session history and score tracking.

    Args:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._db_path = db_path or DB_PATH
        self._init_db()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_session(
        self,
        user_name: str,
        role: str,
        experience_level: str,
        interview_type: str,
        company_type: str,
        overall_score: float,
        questions_attempted: int,
        notes: str = "",
    ) -> int:
        """Create a new session record and return its session_id.

        Args:
            user_name:            Candidate's name.
            role:                 Target role.
            experience_level:     Experience band.
            interview_type:       Technical / Soft Skills / Mixed.
            company_type:         Target company type.
            overall_score:        Average score for this session.
            questions_attempted:  Number of questions answered.
            notes:                Optional free-form notes.

        Returns:
            Auto-generated session_id (integer).
        """
        created_at = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions
                (user_name, role, experience_level, interview_type, company_type,
                 created_at, overall_score, questions_attempted, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_name, role, experience_level, interview_type, company_type,
                 created_at, overall_score, questions_attempted, notes),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def save_question_score(
        self,
        session_id: int,
        question_id: str,
        question_text: str,
        category: str,
        user_answer: str,
        overall_score: float,
        dimension_scores: dict[str, int],
        strengths: list[str],
        gaps: list[str],
    ) -> int:
        """Save a per-question evaluation result.

        Returns:
            Auto-generated score_id.
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO question_scores
                (session_id, question_id, question_text, category, user_answer,
                 overall_score, dimension_scores_json, strengths_json, gaps_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    question_id,
                    question_text[:500],
                    category,
                    user_answer[:2000],
                    overall_score,
                    json.dumps(dimension_scores),
                    json.dumps(strengths),
                    json.dumps(gaps),
                ),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def get_sessions(self, user_name: Optional[str] = None, limit: int = 50) -> list[Session]:
        """Retrieve recent sessions, optionally filtered by user name.

        Args:
            user_name: Filter by name (None = all sessions).
            limit:     Maximum number of sessions to return (most recent first).

        Returns:
            List of :class:`Session` objects.
        """
        query = "SELECT * FROM sessions"
        params: list = []
        if user_name:
            query += " WHERE LOWER(user_name) = LOWER(?)"
            params.append(user_name)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [_row_to_session(r) for r in rows]

    def get_question_scores(self, session_id: int) -> list[QuestionScore]:
        """Retrieve all question scores for a given session.

        Args:
            session_id: ID of the session.

        Returns:
            List of :class:`QuestionScore` objects.
        """
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM question_scores WHERE session_id = ? ORDER BY score_id",
                (session_id,),
            ).fetchall()
        return [_row_to_question_score(r) for r in rows]

    def get_progress_data(
        self, user_name: Optional[str] = None, limit: int = 20
    ) -> list[dict]:
        """Return session-level progress data for charting.

        Returns:
            List of dicts with keys: ``date``, ``score``, ``role``, ``questions_attempted``.
        """
        sessions = self.get_sessions(user_name=user_name, limit=limit)
        return [
            {
                "date": s.created_at[:10],
                "score": s.overall_score,
                "role": s.role,
                "questions_attempted": s.questions_attempted,
            }
            for s in reversed(sessions)  # chronological order for chart
        ]

    def get_dimension_averages(
        self, user_name: Optional[str] = None, limit_sessions: int = 10
    ) -> dict[str, float]:
        """Compute average scores per rubric dimension across recent sessions.

        Returns:
            Dict mapping dimension name to average score.
        """
        sessions = self.get_sessions(user_name=user_name, limit=limit_sessions)
        dim_totals: dict[str, list[float]] = {}
        for session in sessions:
            if session.session_id is None:
                continue
            scores = self.get_question_scores(session.session_id)
            for qs in scores:
                try:
                    dims = json.loads(qs.dimension_scores_json)
                    for dim, val in dims.items():
                        dim_totals.setdefault(dim, []).append(float(val))
                except (json.JSONDecodeError, TypeError):
                    pass

        return {
            dim: round(sum(vals) / len(vals), 1)
            for dim, vals in dim_totals.items()
            if vals
        }

    def delete_session(self, session_id: int) -> None:
        """Delete a session and its question scores."""
        with self._conn() as conn:
            conn.execute("DELETE FROM question_scores WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    # ------------------------------------------------------------------
    # Database initialisation
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create tables if they do not exist."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name           TEXT NOT NULL DEFAULT '',
                    role                TEXT NOT NULL,
                    experience_level    TEXT NOT NULL,
                    interview_type      TEXT NOT NULL,
                    company_type        TEXT NOT NULL DEFAULT 'Any',
                    created_at          TEXT NOT NULL,
                    overall_score       REAL NOT NULL DEFAULT 0.0,
                    questions_attempted INTEGER NOT NULL DEFAULT 0,
                    notes               TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS question_scores (
                    score_id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id              INTEGER NOT NULL,
                    question_id             TEXT NOT NULL,
                    question_text           TEXT NOT NULL,
                    category                TEXT NOT NULL,
                    user_answer             TEXT NOT NULL DEFAULT '',
                    overall_score           REAL NOT NULL DEFAULT 0.0,
                    dimension_scores_json   TEXT NOT NULL DEFAULT '{}',
                    strengths_json          TEXT NOT NULL DEFAULT '[]',
                    gaps_json               TEXT NOT NULL DEFAULT '[]',
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
                """
            )

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that provides an auto-committing SQLite connection."""
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_store_singleton: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Return the module-level :class:`SessionStore` singleton."""
    global _store_singleton
    if _store_singleton is None:
        _store_singleton = SessionStore()
    return _store_singleton


# ---------------------------------------------------------------------------
# Row mapping helpers
# ---------------------------------------------------------------------------

def _row_to_session(row: sqlite3.Row) -> Session:
    return Session(
        session_id=row["session_id"],
        user_name=row["user_name"],
        role=row["role"],
        experience_level=row["experience_level"],
        interview_type=row["interview_type"],
        company_type=row["company_type"],
        created_at=row["created_at"],
        overall_score=row["overall_score"],
        questions_attempted=row["questions_attempted"],
        notes=row["notes"],
    )


def _row_to_question_score(row: sqlite3.Row) -> QuestionScore:
    return QuestionScore(
        score_id=row["score_id"],
        session_id=row["session_id"],
        question_id=row["question_id"],
        question_text=row["question_text"],
        category=row["category"],
        user_answer=row["user_answer"],
        overall_score=row["overall_score"],
        dimension_scores_json=row["dimension_scores_json"],
        strengths_json=row["strengths_json"],
        gaps_json=row["gaps_json"],
    )
