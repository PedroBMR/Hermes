"""Entrypoint for running Hermes as a module."""

from .config import load_from_args
from .logging import setup_logging
from .ui import gui
from .services.reminders import start_scheduler


def main(argv: list[str] | None = None) -> None:
    """Launch the graphical user interface."""
    setup_logging()
    load_from_args(argv)
    start_scheduler()
    gui.main()


if __name__ == "__main__":
    main()
