import sqlite3

from hermes.data.migrate import migrate_to_v2


def test_migrate_to_v2_preserves_rows_and_adds_columns(tmp_path):
    db_file = tmp_path / "legacy.db"
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE ideias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                texto TEXT NOT NULL,
                data TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO ideias (usuario_id, texto, data) VALUES (?, ?, ?)",
            (1, "old", "2023-01-01")
        )
    migrate_to_v2(str(db_file))
    with sqlite3.connect(db_file) as conn:
        cur = conn.execute(
            "SELECT usuario_id, texto, data, source, llm_summary, llm_topic, tags FROM ideias"
        )
        rows = cur.fetchall()
        assert rows == [(1, "old", "2023-01-01", None, None, None, None)]
        cur = conn.execute("PRAGMA table_info(ideias)")
        cols = {row[1] for row in cur.fetchall()}
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'"
        )
        assert cur.fetchone() is not None
    assert {
        "usuario_id",
        "texto",
        "data",
        "source",
        "llm_summary",
        "llm_topic",
        "tags",
    }.issubset(cols)
