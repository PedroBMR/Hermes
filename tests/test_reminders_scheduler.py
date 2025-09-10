from datetime import datetime, timedelta
import types
import sys
import importlib
import pathlib

import pytest
from tests import requests_stub  # noqa: F401 ensure 'requests' stub


class DummyScheduler:
    """Simplistic scheduler that stores jobs and allows manual execution."""

    def __init__(self):
        self.jobs: list[tuple] = []

    def start(self):
        pass

    def add_job(self, func, trigger, run_date, args, id, replace_existing):
        self.jobs.append((func, args))

    def run_jobs(self):
        for func, args in self.jobs:
            func(*args)


# Stub external dependencies
sys.modules['requests.adapters'] = types.ModuleType('requests.adapters')
sys.modules['requests.adapters'].HTTPAdapter = object
sys.modules['urllib3'] = types.ModuleType('urllib3')
sys.modules['urllib3.util'] = types.ModuleType('urllib3.util')
sys.modules['urllib3.util.retry'] = types.ModuleType('urllib3.util.retry')
sys.modules['urllib3.util.retry'].Retry = object

background = types.ModuleType("apscheduler.schedulers.background")
background.BackgroundScheduler = DummyScheduler
sys.modules.setdefault("apscheduler", types.ModuleType("apscheduler"))
sys.modules.setdefault("apscheduler.schedulers", types.ModuleType("apscheduler.schedulers"))
sys.modules["apscheduler.schedulers.background"] = background

services_pkg = types.ModuleType("hermes.services")
services_pkg.__path__ = [
    str(
        pathlib.Path(__file__).resolve().parent.parent
        / "src"
        / "hermes"
        / "services"
    )
]
sys.modules["hermes.services"] = services_pkg

from hermes.config import config
db = importlib.import_module("hermes.services.db")
reminders = importlib.import_module("hermes.services.reminders")


@pytest.fixture
def reminder_env(tmp_path, monkeypatch):
    db_file = tmp_path / "reminders.db"
    monkeypatch.setattr(config, "DB_PATH", str(db_file))
    monkeypatch.setattr(db, "DB_PATH", str(db_file))
    db.init_db()
    user_id = db.add_user("Alice", "tipo")

    scheduler = DummyScheduler()
    monkeypatch.setattr(reminders, "BackgroundScheduler", lambda: scheduler)

    alerts: list[str] = []
    monkeypatch.setattr(reminders, "_alert", lambda msg: alerts.append(msg))

    yield user_id, scheduler, alerts
    reminders._scheduler = None


def test_reminder_trigger_and_listing(reminder_env):
    user_id, scheduler, alerts = reminder_env
    trigger_at = (datetime.utcnow() + timedelta(minutes=1)).isoformat()

    reminder_id = db.add_reminder(user_id, "Ping", trigger_at)

    pending = db.list_reminders(user_id)
    assert pending == [
        {
            "id": reminder_id,
            "user_id": user_id,
            "message": "Ping",
            "trigger_at": trigger_at,
            "triggered_at": None,
        }
    ]

    reminders.start_scheduler()
    assert len(scheduler.jobs) == 1

    scheduler.run_jobs()

    assert alerts == ["Ping"]

    listed = db.list_reminders(user_id)
    assert listed[0]["id"] == reminder_id
    assert listed[0]["triggered_at"] is not None

    assert db.list_reminders(user_id, only_pending=True) == []
