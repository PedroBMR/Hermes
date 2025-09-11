from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from .db import list_reminders, list_users, mark_triggered

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _alert(message: str) -> None:
    """Notify the user about a triggered reminder."""
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception:  # pragma: no cover - best effort
        logger.info("Reminder: %s", message)


def _run_reminder(reminder_id: int, message: str) -> None:
    """Mark reminder as triggered and alert the user."""
    mark_triggered(reminder_id)
    _alert(message)


def _schedule_reminder(reminder: dict) -> None:
    if _scheduler is None:
        return
    run_date = datetime.fromisoformat(reminder["trigger_at"])
    _scheduler.add_job(
        _run_reminder,
        "date",
        run_date=run_date,
        args=[reminder["id"], reminder["message"]],
        id=f"reminder-{reminder['id']}",
        replace_existing=True,
    )


def load_pending_reminders() -> None:
    """Fetch pending reminders from the database and schedule them."""
    if _scheduler is None:
        return
    for user in list_users():
        for reminder in list_reminders(user["id"], only_pending=True):
            _schedule_reminder(reminder)


def start_scheduler() -> BackgroundScheduler:
    """Start the reminder scheduler and load pending reminders."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    _scheduler = BackgroundScheduler()
    _scheduler.start()
    load_pending_reminders()
    return _scheduler
