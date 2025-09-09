import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_TOKEN", "secret")
    db_file = tmp_path / "api.db"

    from hermes.services import db as dao

    monkeypatch.setattr(dao, "DB_PATH", str(db_file))

    from hermes import api as api_module

    with TestClient(api_module.app) as client:
        yield client, api_module, str(db_file)


def test_health(api_client):
    client, _, _ = api_client
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_create_idea_sources_device(api_client):
    client, _, db_path = api_client
    res = client.post(
        "/ideas",
        json={"user": 1, "title": "T", "body": "B"},
        headers={"X-Token": "secret", "X-Device-Id": "dev1"},
    )
    assert res.status_code == 200
    assert res.json()["source"] == "caduceu_dev1"
    with sqlite3.connect(db_path) as conn:
        source = conn.execute("SELECT source FROM ideias").fetchone()[0]
    assert source == "caduceu_dev1"


def test_ask_returns_response(api_client, monkeypatch):
    client, api_module, _ = api_client

    def fake(prompt):
        return {"ok": True, "response": "hi"}

    monkeypatch.setattr(api_module, "gerar_resposta", fake)
    res = client.post(
        "/ask", json={"prompt": "hello"}, headers={"X-Token": "secret"}
    )
    assert res.status_code == 200
    assert res.json() == {"response": "hi"}
