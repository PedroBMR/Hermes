"""Minimal stub for :mod:`urllib3` used in tests."""

import sys
import types


urllib3_module = types.ModuleType("urllib3")
util_module = types.ModuleType("urllib3.util")
retry_module = types.ModuleType("urllib3.util.retry")


class Retry:
    def __init__(
        self,
        total=None,
        backoff_factor=None,
        status_forcelist=None,
        allowed_methods=None,
    ) -> None:
        self.total = total
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.allowed_methods = allowed_methods


retry_module.Retry = Retry
util_module.retry = retry_module
urllib3_module.util = util_module


sys.modules.setdefault("urllib3", urllib3_module)
sys.modules.setdefault("urllib3.util", util_module)
sys.modules.setdefault("urllib3.util.retry", retry_module)


__all__ = ["Retry"]

