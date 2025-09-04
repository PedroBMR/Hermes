"""Central configuration for Hermes.

This module exposes a global :data:`config` instance whose values can be
customised via environment variables or command-line arguments.
"""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from typing import Sequence


@dataclass
class Config:
    """Holds application configuration values."""

    DB_PATH: str = "hermes.db"
    API_PORT: int = 11434
    OLLAMA_MODEL: str = "mistral"
    TIMEOUT: int = 30  # seconds


logger = logging.getLogger(__name__)


def _safe_int(value: str | None, default: int, name: str) -> int:
    """Safely convert ``value`` to ``int``.

    Logs a warning and returns ``default`` if conversion fails.
    """
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        logger.warning("Invalid %s %r; using %d", name, value, default)
        return default


def _from_env() -> Config:
    """Create a :class:`Config` instance from environment variables."""
    return Config(
        DB_PATH=os.getenv("HERMES_DB_PATH", Config.DB_PATH),
        API_PORT=_safe_int(
            os.getenv("HERMES_API_PORT"), Config.API_PORT, "HERMES_API_PORT"
        ),
        OLLAMA_MODEL=os.getenv("HERMES_OLLAMA_MODEL", Config.OLLAMA_MODEL),
        TIMEOUT=_safe_int(
            os.getenv("HERMES_TIMEOUT"), Config.TIMEOUT, "HERMES_TIMEOUT"
        ),
    )


config = _from_env()


def load_from_args(args: Sequence[str] | None = None) -> Config:
    """Update :data:`config` using command-line arguments.

    Parameters
    ----------
    args: Sequence[str] | None
        Argument list (excluding the program name). If ``None`` the current
        ``sys.argv`` is used.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--db-path")
    parser.add_argument("--api-port")
    parser.add_argument("--ollama-model")
    parser.add_argument("--timeout")

    namespace, _ = parser.parse_known_args(args)

    global config
    config = Config(
        DB_PATH=namespace.db_path or config.DB_PATH,
        API_PORT=_safe_int(namespace.api_port, config.API_PORT, "--api-port"),
        OLLAMA_MODEL=namespace.ollama_model or config.OLLAMA_MODEL,
        TIMEOUT=_safe_int(namespace.timeout, config.TIMEOUT, "--timeout"),
    )
    return config
