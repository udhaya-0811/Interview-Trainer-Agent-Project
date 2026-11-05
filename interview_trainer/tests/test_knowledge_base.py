"""
test_knowledge_base.py – Tests for knowledge-base chunking and retrieval.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from interview_trainer.core.knowledge_base import (
    Chunk,
    KnowledgeBase,
    RetrievalResult,
    _cosine_similarity_batch,
    _infer_category,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_MD = """# Java Developer KB

---
## Q1 | difficulty: beginner
**Question:** What is OOP?

**Answer:**
OOP stands for Object-Oriented Programming with four pillars: Encapsulation,
Abstraction, Inheritance, Polymorphism.

---
## Q2 | difficulty: intermediate
**Question:** What is the difference between ArrayList and LinkedList?

**Answer:**
ArrayList uses a dynamic array; LinkedList uses a doubly-linked list.
ArrayList is O(1) for random access; LinkedList is O(1) for insertions.

---
## B1 | difficulty: intermediate
**Question:** Tell me about a challenge you faced.

**Answer:**
**Situation:** ... **Task:** ... **Action:** ... **Result:** ...
"""

BEHAVIORAL_MD = """# Behavioral STAR Guide

---
## B1 | difficulty: intermediate
**Question:** Describe a time you solved a hard problem.

**Answer:**
**Situation:** We had a production outage.
**Task:** Find and fix root cause.
**Action:** Added logging, identified DB deadlock.
**Result:** Fixed in 2 hours.
"""


@pytest.fixture
def temp_kb_dir(tmp_path: Path) -> Path:
    """Create a temporary knowledge-base directory with sample files."""
    (tmp_path / "java_developer.md").write_text(SAMPLE_MD)
    (tmp_path / "behavioral_star.md").write_text(BEHAVIORAL_MD)
    return tmp_path


def _build_kb_with_mocked_embeddings(kb_dir: Path) -> KnowledgeBase:
    """Build a KnowledgeBase with embedding methods patched (no sentence-transformers needed)."""
    kb = KnowledgeBase(kb_dir=kb_dir)
    # Patch both methods that call the model so no sentence-transformers import is needed
    kb._embed_chunks = lambda chunks: np.random.rand(len(chunks), 384).astype("float32")  # type: ignore[method-assign]
    kb._embed_text = lambda text: np.random.rand(384).astype("float32")  # type: ignore[method-assign]
    kb.build()
    return kb


# ---------------------------------------------------------------------------
# Chunking tests
# ---------------------------------------------------------------------------

class TestChunking:
    def test_chunks_java_file(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        assert len(kb.chunks) >= 3  # Q1, Q2, B1

    def test_chunk_has_correct_role(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        java_chunks = [c for c in kb.chunks if c.role == "java_developer"]
        assert len(java_chunks) >= 2

    def test_behavioral_chunk_categorised_correctly(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        behavioral_chunks = [c for c in kb.chunks if c.category == "behavioral"]
        assert len(behavioral_chunks) >= 1

    def test_chunk_difficulty_parsed(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        difficulties = {c.difficulty for c in kb.chunks}
        assert "beginner" in difficulties
        assert "intermediate" in difficulties

    def test_chunk_question_text_extracted(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        java_chunks = [c for c in kb.chunks if c.role == "java_developer"]
        q_texts = [c.question_text for c in java_chunks]
        assert any("OOP" in qt for qt in q_texts)


# ---------------------------------------------------------------------------
# Retrieval tests
# ---------------------------------------------------------------------------

class TestRetrieval:
    def test_retrieval_returns_results(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        results = kb.retrieve("OOP concepts", top_k=2)
        assert len(results) > 0
        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_retrieval_respects_top_k(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        results = kb.retrieve("Java interview", top_k=1)
        assert len(results) <= 1

    def test_role_filter_excludes_other_roles(self, temp_kb_dir: Path):
        kb = _build_kb_with_mocked_embeddings(temp_kb_dir)
        results = kb.retrieve("Python", role="data_analyst", top_k=5)
        # Should not return java_developer chunks (behavioral/hr are always included)
        for r in results:
            assert r.chunk.role in ("data_analyst", "behavioral_star", "hr_guidelines", "soft_skills")

    def test_empty_kb_returns_empty(self, tmp_path: Path):
        """Empty KB directory should not crash."""
        kb = _build_kb_with_mocked_embeddings(tmp_path)
        assert kb.chunks == []
        results = kb.retrieve("anything")
        assert results == []


# ---------------------------------------------------------------------------
# Cosine similarity
# ---------------------------------------------------------------------------

class TestCosineSimilarity:
    def test_identical_vectors_score_1(self):
        v = np.array([1.0, 0.0, 0.0], dtype="float32")
        scores = _cosine_similarity_batch(v, np.array([v]))
        assert scores[0] == pytest.approx(1.0, abs=1e-5)

    def test_orthogonal_vectors_score_0(self):
        v1 = np.array([1.0, 0.0], dtype="float32")
        v2 = np.array([[0.0, 1.0]], dtype="float32")
        scores = _cosine_similarity_batch(v1, v2)
        assert scores[0] == pytest.approx(0.0, abs=1e-5)


# ---------------------------------------------------------------------------
# Category inference
# ---------------------------------------------------------------------------

class TestInferCategory:
    def test_behavioral(self):
        assert _infer_category("behavioral_star", "behavioral_star.md") == "behavioral"

    def test_hr(self):
        assert _infer_category("hr_guidelines", "hr_guidelines.md") == "hr"

    def test_technical_default(self):
        assert _infer_category("java_developer", "java_developer.md") == "technical"
