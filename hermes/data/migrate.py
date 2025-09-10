import argparse
import sqlite3
from typing import Sequence

from ..config import config

# Columns introduced in schema version 2
V2_COLUMNS = {
    "source": "TEXT",
    "llm_summary": "TEXT",
    "llm_topic": "TEXT",
    "tags": "TEXT",
}

REMINDERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    trigger_at TEXT NOT NULL,
    triggered_at TEXT,
    FOREIGN KEY(user_id) REFERENCES usuarios(id)
)
"""


def migrate_to_v2(db_path: str) -> None:
    """Upgrade the database at ``db_path`` to the v2 schema.

    The migration adds any missing columns declared in :data:`V2_COLUMNS` to the
    ``ideias`` table. It is safe to run multiple times as existing columns are
    left untouched.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(ideias)")
        existing = {row[1] for row in cursor.fetchall()}

        for column, col_type in V2_COLUMNS.items():
            if column not in existing:
                cursor.execute(f"ALTER TABLE ideias ADD COLUMN {column} {col_type}")

        cursor.execute(REMINDERS_TABLE_SQL)


def main(argv: Sequence[str] | None = None) -> None:
    """Command-line entry point to run the migration manually."""
    parser = argparse.ArgumentParser(description="Migrate Hermes DB to v2 schema")
    parser.add_argument("--db-path", default=config.DB_PATH, help="Path to the SQLite DB")
    args = parser.parse_args(argv)
    migrate_to_v2(args.db_path)


if __name__ == "__main__":
    main()
