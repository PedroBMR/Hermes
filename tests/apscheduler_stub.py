"""Minimal stub for :mod:`apscheduler` used in tests."""

import sys
import types


apscheduler = types.ModuleType("apscheduler")
schedulers = types.ModuleType("apscheduler.schedulers")
background = types.ModuleType("apscheduler.schedulers.background")


class BackgroundScheduler:
    def add_job(self, *args, **kwargs):  # pragma: no cover - no-op
        pass

    def start(self) -> None:  # pragma: no cover - no-op
        pass

    def shutdown(self, *args, **kwargs):  # pragma: no cover - no-op
        pass


background.BackgroundScheduler = BackgroundScheduler
schedulers.background = background
apscheduler.schedulers = schedulers


sys.modules.setdefault("apscheduler", apscheduler)
sys.modules.setdefault("apscheduler.schedulers", schedulers)
sys.modules.setdefault("apscheduler.schedulers.background", background)


__all__ = ["BackgroundScheduler"]

