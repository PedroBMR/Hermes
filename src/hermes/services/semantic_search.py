"""Semantic search utilities for Hermes.

The :mod:`semantic_search` module exposes a small pluggable interface,
``VectorIndex``, used to build and query vector representations of ideas.
The default implementation relies on scikit-learn's TF-IDF vectorizer, but
alternative backends such as `FAISS <https://github.com/facebookresearch/faiss>`_
or `Chroma <https://github.com/chroma-core/chroma>`_ can be integrated by
providing another ``VectorIndex`` implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Protocol, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .db import search_ideas


class VectorIndex(Protocol):
    """Interface for vector search backends.

    Any backend providing semantic search capabilities must implement this
    protocol.  Only two methods are required: :meth:`fit` to build the index
    from raw documents and :meth:`search` to return the most similar document
    identifiers for a query string.
    """

    def fit(self, documents: Iterable[str], ids: Iterable[int]) -> None:
        """Build the index from ``documents`` associated with ``ids``."""

        ...

    def search(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
        """Return ``limit`` document ids ranked by similarity to ``query``."""

        ...


@dataclass
class TfidfVectorIndex:
    """Simple in-memory vector index using scikit-learn's TF-IDF.

    This serves as the default backend used by :func:`semantic_search`.  It is
    intentionally lightweight and provides only the minimal functionality
    required.  Custom indexes (e.g. FAISS or Chroma) can replace this class by
    implementing the :class:`VectorIndex` protocol and passing an instance to
    :func:`semantic_search`.
    """

    vectorizer: TfidfVectorizer = field(default_factory=TfidfVectorizer)
    matrix: any | None = None
    ids: List[int] = field(default_factory=list)

    def fit(self, documents: Iterable[str], ids: Iterable[int]) -> None:
        self.matrix = self.vectorizer.fit_transform(list(documents))
        self.ids = list(ids)

    def search(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
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
    user_id: int,
    limit: int = 10,
    index: VectorIndex | None = None,
) -> list[dict]:
    """Search ideas semantically using cosine similarity over TF-IDF vectors.

    Parameters
    ----------
    query: str
        Text to search for.
    user_id: int
        Restrict search to ideas from this user.
    limit: int, default ``10``
        Maximum number of ideas to return.
    index: VectorIndex | None, optional
        Custom backend implementing :class:`VectorIndex`.  When ``None`` a
        :class:`TfidfVectorIndex` instance is used.

    Returns
    -------
    list[dict]
        Idea dictionaries ordered by semantic similarity.
    """

    if user_id is None:
        raise ValueError("user_id is required for semantic_search")

    ideas = search_ideas(user_id)
    if not ideas:
        return []

    id_map = {idea["id"]: idea for idea in ideas}
    documents = [_idea_to_text(idea) for idea in ideas]
    ids = list(id_map.keys())

    backend = index or TfidfVectorIndex()
    backend.fit(documents, ids)
    ranked = backend.search(query, limit)

    return [id_map[i] for i, _ in ranked]


__all__ = ["semantic_search", "VectorIndex", "TfidfVectorIndex"]

