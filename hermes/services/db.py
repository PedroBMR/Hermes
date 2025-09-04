"""SQLite-based Data Access Object for Hermes ideas.

This module provides simple helper functions to interact with the
``ideias`` table using the schema v2.  It mirrors part of the previous
``hermes.data.database`` API but returns dictionaries instead of tuples
and exposes CRUD operations for ideas.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Iterable

from ..config import config

DB_PATH = config.DB_PATH

# Columns allowed to be updated via :func:`update_idea`
IDEIA_COLUMNS = {
    "user_id",
    "title",
    "body",
    "source",
    "llm_summary",
    "llm_topic",
    "tags",
}


def _dicts(cursor: sqlite3.Cursor, rows: Iterable[sqlite3.Row]) -> list[dict]:
    """Convert ``sqlite3.Row`` objects to plain dictionaries."""

    return [dict(row) for row in rows]


def add_idea(
    user_id: int,
    title: str,
    body: str,
    source: str | None = None,
    llm_summary: str | None = None,
    llm_topic: str | None = None,
    tags: str | None = None,
) -> int:
    """Insert a new idea and return its ``id``."""

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ideias (
                user_id,
                title,
                body,
                source,
                llm_summary,
                llm_topic,
                tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, body, source, llm_summary, llm_topic, tags),
        )
        return int(cursor.lastrowid)


def update_idea(idea_id: int, **fields: Any) -> None:
    """Update columns of ``ideias`` for ``idea_id``.

    Only known columns present in ``fields`` are updated. Passing no valid
    columns results in a no-op.
    """

    cols = [col for col in fields.keys() if col in IDEIA_COLUMNS]
    if not cols:
        return

    assignments = ", ".join(f"{col} = ?" for col in cols)
    params = [fields[col] for col in cols]
    params.append(idea_id)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE ideias SET {assignments} WHERE id = ?", params)


def delete_idea(idea_id: int) -> None:
    """Remove an idea from the database."""

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ideias WHERE id = ?", (idea_id,))


def list_ideas(user_id: int) -> list[dict]:
    """Return a list of ideas for ``user_id`` ordered by ``created_at`` desc."""

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, title, body, source, created_at, llm_summary,
                   llm_topic, tags
            FROM ideias
            WHERE user_id = ?
            ORDER BY datetime(created_at) DESC
            """,
            (user_id,),
        )
        return _dicts(cursor, cursor.fetchall())


def search_ideas(
    user_id: int | None = None,
    text: str | None = None,
    topic: str | None = None,
    tag: str | None = None,
) -> list[dict]:
    """Search ideas using simple ``LIKE``/``INSTR`` filters.

    Parameters are optional and combined using ``AND`` when provided. The
    returned list is ordered by ``created_at`` descending.
    """

    conditions = []
    params: list[Any] = []

    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(user_id)
    if text:
        like = f"%{text}%"
        conditions.append(
            "(title LIKE ? OR body LIKE ? OR IFNULL(llm_summary, '') LIKE ?)"
        )
        params.extend([like, like, like])
    if topic:
        conditions.append("IFNULL(llm_topic, '') LIKE ?")
        params.append(f"%{topic}%")
    if tag:
        # Look for tag inside comma-separated list
        conditions.append(
            "INSTR(',' || IFNULL(tags, '') || ',', ',' || ? || ',') > 0"
        )
        params.append(tag)

    query = (
        "SELECT id, user_id, title, body, source, created_at, llm_summary, "
        "llm_topic, tags FROM ideias"
    )
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY datetime(created_at) DESC"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        return _dicts(cursor, cursor.fetchall())
