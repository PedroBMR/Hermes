import sqlite3

import pytest

from hermes.services import db as dao


@pytest.fixture
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "dao.db"
    monkeypatch.setattr(dao, "DB_PATH", str(db_file))
    dao.init_db(str(db_file))
    user_id = dao.add_user("Alice", "tipo")
    return user_id, str(db_file)


def test_add_idea_inserts_row(setup_db):
    user_id, db_path = setup_db
    idea_id = dao.add_idea(user_id, "Title", "Body", source="web")
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, user_id, title, body, source FROM ideias"
        ).fetchone()
    assert row == (idea_id, user_id, "Title", "Body", "web")


def test_update_idea_updates_row(setup_db):
    user_id, db_path = setup_db
    idea_id = dao.add_idea(user_id, "Old", "Body")
    dao.update_idea(idea_id, title="New", tags="one,two")
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT title, tags FROM ideias WHERE id = ?", (idea_id,)
        ).fetchone()
    assert row == ("New", "one,two")


def test_delete_idea_removes_row(setup_db):
    user_id, db_path = setup_db
    idea_id = dao.add_idea(user_id, "T", "B")
    dao.delete_idea(idea_id)
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM ideias").fetchone()[0]
    assert count == 0


def test_list_ideas_orders_by_created_at(setup_db):
    user_id, db_path = setup_db
    first = dao.add_idea(user_id, "First", "B1")
    second = dao.add_idea(user_id, "Second", "B2")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE ideias SET created_at = '2000-01-01T00:00:00' WHERE id = ?",
            (first,)
        )
    ideas = dao.list_ideas(user_id)
    assert [idea["id"] for idea in ideas] == [second, first]


def test_search_ideas_filters(setup_db):
    user_id, db_path = setup_db
    first = dao.add_idea(
        user_id, "AI Title", "about AI", llm_topic="ai", tags="tech,ai"
    )
    second = dao.add_idea(
        user_id, "Music", "about music", llm_topic="music", tags="art"
    )
    other_user = dao.add_user("Bob", "tipo")
    third = dao.add_idea(other_user, "Other", "body", llm_topic="ai", tags="tech")

    res = dao.search_ideas(user_id=user_id, text="AI")
    assert [r["id"] for r in res] == [first]

    res = dao.search_ideas(user_id=user_id, topic="music")
    assert [r["id"] for r in res] == [second]

    res = dao.search_ideas(user_id=user_id, tag="tech")
    assert {r["id"] for r in res} == {first}

    res = dao.search_ideas(user_id=user_id)
    assert {r["id"] for r in res} == {first, second}


def test_reminder_crud(setup_db):
    user_id, db_path = setup_db
    rid = dao.add_reminder(user_id, "Call Bob", "2030-01-01T10:00:00")
    reminders = dao.list_reminders(user_id)
    assert reminders == [
        {
            "id": rid,
            "user_id": user_id,
            "message": "Call Bob",
            "trigger_at": "2030-01-01T10:00:00",
            "triggered_at": None,
        }
    ]
    dao.mark_triggered(rid, "2030-01-01T10:05:00")
    with sqlite3.connect(db_path) as conn:
        trig = conn.execute(
            "SELECT triggered_at FROM reminders WHERE id = ?", (rid,)
        ).fetchone()[0]
    assert trig == "2030-01-01T10:05:00"
