"""
knowledge_base.py – Load, chunk, embed, and retrieve knowledge-base documents.

Uses sentence-transformers (all-MiniLM-L6-v2) for local embeddings and
FAISS for vector storage and similarity search.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A single text chunk with provenance metadata."""

    text: str
    source_file: str            # e.g. "java_developer.md"
    role: str                   # e.g. "java_developer"
    category: str               # e.g. "technical", "behavioral", "hr"
    difficulty: str             # e.g. "beginner", "intermediate", "advanced"
    question_id: str            # e.g. "Q1", "B3", "H5"
    question_text: str          # extracted question line for display
    chunk_id: int = 0


@dataclass
class RetrievalResult:
    """A retrieved chunk with its similarity score."""

    chunk: Chunk
    score: float


# ---------------------------------------------------------------------------
# KnowledgeBase class
# ---------------------------------------------------------------------------

class KnowledgeBase:
    """Manages loading, chunking, embedding, and retrieval of the knowledge base.

    Usage::

        kb = KnowledgeBase()
        kb.build()
        results = kb.retrieve("How does JVM garbage collection work?", role="java_developer", top_k=5)
    """

    def __init__(
        self,
        kb_dir: Optional[Path] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        from interview_trainer.config import KNOWLEDGE_BASE_DIR, EMBEDDING_MODEL

        self._kb_dir = kb_dir or KNOWLEDGE_BASE_DIR
        self._embedding_model_name = embedding_model or EMBEDDING_MODEL
        self._chunks: list[Chunk] = []
        self._embeddings: Optional[np.ndarray] = None
        self._model = None  # sentence-transformers model (lazy loaded)
        self._built = False

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Load all knowledge-base files, chunk them, and build the FAISS index."""
        logger.info("Building knowledge base from %s", self._kb_dir)
        raw_chunks = self._load_and_chunk_all()
        self._chunks = raw_chunks
        self._embeddings = self._embed_chunks(raw_chunks)
        self._built = True
        logger.info("Knowledge base built: %d chunks indexed.", len(self._chunks))

    def retrieve(
        self,
        query: str,
        role: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """Retrieve the top-k most relevant chunks for a query.

        Args:
            query:    Natural language query.
            role:     Optional role filter (e.g. "java_developer").
            category: Optional category filter ("technical", "behavioral", "hr").
            top_k:    Number of results to return.

        Returns:
            List of :class:`RetrievalResult` ordered by descending similarity.
        """
        if not self._built:
            self.build()

        # Filter candidates by metadata
        candidates, candidate_indices = self._filter_chunks(role, category)
        if not candidates:
            return []

        # Embed query
        q_emb = self._embed_text(query)

        # Compute cosine similarity
        candidate_embs = self._embeddings[candidate_indices]  # type: ignore[index]
        scores = _cosine_similarity_batch(q_emb, candidate_embs)

        # Rank and return top-k
        top_indices = np.argsort(scores)[::-1][:top_k]
        results: list[RetrievalResult] = []
        for idx in top_indices:
            original_idx = candidate_indices[idx]
            results.append(
                RetrievalResult(
                    chunk=self._chunks[original_idx],
                    score=float(scores[idx]),
                )
            )
        return results

    @property
    def chunks(self) -> list[Chunk]:
        """All loaded chunks (built or empty)."""
        return self._chunks

    # ------------------------------------------------------------------
    # Loading and chunking
    # ------------------------------------------------------------------

    def _load_and_chunk_all(self) -> list[Chunk]:
        """Walk the knowledge-base directory and chunk every Markdown file."""
        chunks: list[Chunk] = []
        for md_file in sorted(self._kb_dir.glob("*.md")):
            try:
                file_chunks = self._chunk_markdown_file(md_file)
                chunks.extend(file_chunks)
                logger.debug("Loaded %d chunks from %s", len(file_chunks), md_file.name)
            except Exception as exc:
                logger.warning("Failed to load %s: %s", md_file.name, exc)
        return chunks

    def _chunk_markdown_file(self, path: Path) -> list[Chunk]:
        """Parse a Markdown file into :class:`Chunk` objects.

        Each ``## Q{n}`` / ``## B{n}`` / ``## H{n}`` / ``## S{n}`` block
        becomes one chunk.
        """
        text = path.read_text(encoding="utf-8")
        role = path.stem  # e.g. "java_developer"
        category = _infer_category(role, path.name)

        # Split on Q/A blocks delimited by `## Q1 | difficulty: ...` headers
        block_pattern = re.compile(
            r"^##\s+(Q\d+|B\d+|H\d+|S\d+)\s*\|?\s*difficulty:\s*(\w+)",
            re.MULTILINE,
        )
        matches = list(block_pattern.finditer(text))

        if not matches:
            # Fallback: treat entire file as one chunk
            return [
                Chunk(
                    text=text[:2000],
                    source_file=path.name,
                    role=role,
                    category=category,
                    difficulty="intermediate",
                    question_id="ALL",
                    question_text=path.stem,
                    chunk_id=0,
                )
            ]

        chunks: list[Chunk] = []
        for i, match in enumerate(matches):
            question_id = match.group(1)
            difficulty = match.group(2).lower()
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block_text = text[start:end].strip()

            # Extract the question line
            q_match = re.search(r"\*\*Question:\*\*\s*(.+)", block_text)
            question_text = q_match.group(1).strip() if q_match else question_id

            # Per-block category refinement
            block_category = category
            if question_id.startswith("B"):
                block_category = "behavioral"
            elif question_id.startswith("H"):
                block_category = "hr"
            elif question_id.startswith("S"):
                block_category = "soft_skills"

            chunks.append(
                Chunk(
                    text=block_text,
                    source_file=path.name,
                    role=role,
                    category=block_category,
                    difficulty=difficulty,
                    question_id=question_id,
                    question_text=question_text,
                    chunk_id=i,
                )
            )
        return chunks

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    def _load_model(self):
        """Lazy-load the sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "sentence-transformers is not installed. "
                    "Run: pip install sentence-transformers"
                ) from exc
            logger.info("Loading embedding model: %s", self._embedding_model_name)
            self._model = SentenceTransformer(self._embedding_model_name)
        return self._model

    def _embed_text(self, text: str) -> np.ndarray:
        model = self._load_model()
        return model.encode([text], normalize_embeddings=True)[0]

    def _embed_chunks(self, chunks: list[Chunk]) -> np.ndarray:
        """Embed all chunks in one batched call for efficiency."""
        model = self._load_model()
        texts = [c.text for c in chunks]
        logger.info("Embedding %d chunks…", len(texts))
        embeddings = model.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.array(embeddings, dtype="float32")

    # ------------------------------------------------------------------
    # Filtering helpers
    # ------------------------------------------------------------------

    def _filter_chunks(
        self,
        role: Optional[str],
        category: Optional[str],
    ) -> tuple[list[Chunk], list[int]]:
        """Return (filtered_chunks, original_indices) applying metadata filters."""
        candidates: list[Chunk] = []
        indices: list[int] = []
        for i, chunk in enumerate(self._chunks):
            if role and chunk.role != role and chunk.role not in (
                "behavioral_star", "hr_guidelines", "soft_skills"
            ):
                continue
            if category and chunk.category != category:
                continue
            candidates.append(chunk)
            indices.append(i)
        return candidates, indices


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_kb_singleton: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    """Return the module-level :class:`KnowledgeBase` singleton, building it on
    first call.
    """
    global _kb_singleton
    if _kb_singleton is None:
        _kb_singleton = KnowledgeBase()
        _kb_singleton.build()
    return _kb_singleton


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cosine_similarity_batch(
    query_emb: np.ndarray, corpus_embs: np.ndarray
) -> np.ndarray:
    """Compute cosine similarity between a query embedding and a corpus matrix.

    Assumes embeddings are already L2-normalised (from SentenceTransformer
    with ``normalize_embeddings=True``).
    """
    return corpus_embs @ query_emb  # dot product == cosine sim for unit vectors


def _infer_category(role_stem: str, filename: str) -> str:
    """Infer a default category from the knowledge-base file stem."""
    mapping = {
        "behavioral_star": "behavioral",
        "hr_guidelines": "hr",
        "soft_skills": "soft_skills",
    }
    return mapping.get(role_stem, "technical")
