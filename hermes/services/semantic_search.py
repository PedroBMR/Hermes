"""Semantic search utilities for Hermes.

This module implements a small vector index based on TF-IDF so that ideas
stored in the database can be searched using cosine similarity.  The
``VectorIndex`` class abstracts the backend so that in the future the
implementation can be replaced by FAISS, Chroma or any other vector store
without changing the public API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .db import list_ideas, search_ideas


@dataclass
class VectorIndex:
    """Simple in-memory vector index using TF-IDF.

    The class is intentionally lightweight and provides only the minimal
    interface needed by :func:`semantic_search`.  Future backends can replace
    this implementation as long as they expose ``fit`` and ``search`` methods
    with the same signatures.
    """

    vectorizer: TfidfVectorizer = field(default_factory=TfidfVectorizer)
    matrix: any | None = None
    ids: List[int] = field(default_factory=list)

    def fit(self, documents: Iterable[str], ids: Iterable[int]) -> None:
        """Build the index from ``documents`` associated with ``ids``."""

        self.matrix = self.vectorizer.fit_transform(list(documents))
        self.ids = list(ids)

    def search(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
        """Return ``limit`` document ids ranked by similarity to ``query``."""

        if not query or self.matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).ravel()
        order = scores.argsort()[::-1][:limit]
        return [(self.ids[i], float(scores[i])) for i in order]


def _idea_to_text(idea: dict) -> str:
    """Combine searchable fields of an idea into a single string."""

    parts = [
        idea.get("title") or "",
        idea.get("body") or "",
        idea.get("llm_summary") or "",
        idea.get("tags") or "",
    ]
    return " ".join(parts)


def semantic_search(
    query: str,
    user_id: int | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search ideas semantically using cosine similarity over TF-IDF vectors.

    Parameters
    ----------
    query: str
        Text to search for.
    user_id: int | None, optional
        If provided, restrict search to ideas from this user.
    limit: int, default ``10``
        Maximum number of ideas to return.

    Returns
    -------
    list[dict]
        Idea dictionaries ordered by semantic similarity.
    """

    ideas = list_ideas(user_id) if user_id is not None else search_ideas()
    if not ideas:
        return []

    id_map = {idea["id"]: idea for idea in ideas}
    documents = [_idea_to_text(idea) for idea in ideas]
    ids = list(id_map.keys())

    index = VectorIndex()
    index.fit(documents, ids)
    ranked = index.search(query, limit)

    return [id_map[i] for i, _ in ranked]


__all__ = ["semantic_search", "VectorIndex"]

