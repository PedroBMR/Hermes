from __future__ import annotations

"""Central configuration for Hermes.

This module exposes a global :data:`config` instance whose values can be
customised via environment variables or command-line arguments.
"""

from dataclasses import dataclass
import os
import argparse
from typing import Sequence


@dataclass
class Config:
    """Holds application configuration values."""

    DB_PATH: str = "hermes.db"
    API_PORT: int = 11434
    OLLAMA_MODEL: str = "mistral"
    TIMEOUT: int = 30  # seconds


def _from_env() -> Config:
    """Create a :class:`Config` instance from environment variables."""
    return Config(
        DB_PATH=os.getenv("HERMES_DB_PATH", Config.DB_PATH),
        API_PORT=int(os.getenv("HERMES_API_PORT", Config.API_PORT)),
        OLLAMA_MODEL=os.getenv("HERMES_OLLAMA_MODEL", Config.OLLAMA_MODEL),
        TIMEOUT=int(os.getenv("HERMES_TIMEOUT", Config.TIMEOUT)),
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
    parser.add_argument("--api-port", type=int)
    parser.add_argument("--ollama-model")
    parser.add_argument("--timeout", type=int)

    namespace, _ = parser.parse_known_args(args)

    global config
    config = Config(
        DB_PATH=namespace.db_path or config.DB_PATH,
        API_PORT=namespace.api_port or config.API_PORT,
        OLLAMA_MODEL=namespace.ollama_model or config.OLLAMA_MODEL,
        TIMEOUT=namespace.timeout or config.TIMEOUT,
    )
    return config
