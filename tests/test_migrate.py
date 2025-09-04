import runpy
import sqlite3
import sys

from hermes.data.migrate import migrate_to_v2


def create_v1_schema(path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE ideias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def test_migrate_adds_columns(tmp_path):
    db = tmp_path / "test.db"
    create_v1_schema(str(db))
    migrate_to_v2(str(db))
    with sqlite3.connect(str(db)) as conn:
        cur = conn.execute("PRAGMA table_info(ideias)")
        cols = {row[1] for row in cur.fetchall()}
    assert {"source", "llm_summary", "llm_topic", "tags"}.issubset(cols)
    migrate_to_v2(str(db))  # idempotent


def test_migration_cli(tmp_path, monkeypatch):
    db = tmp_path / "cli.db"
    create_v1_schema(str(db))
    monkeypatch.setattr(sys, "argv", ["migrate", "--db-path", str(db)])
    runpy.run_module("hermes.data.migrate", run_name="__main__")
    with sqlite3.connect(str(db)) as conn:
        cur = conn.execute("PRAGMA table_info(ideias)")
        cols = {row[1] for row in cur.fetchall()}
    assert {"source", "llm_summary", "llm_topic", "tags"}.issubset(cols)
