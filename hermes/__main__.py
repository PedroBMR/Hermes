"""Entrypoint for running Hermes as a module."""

from .config import load_from_args
from .logging import setup_logging
from .ui import gui


def main(argv: list[str] | None = None) -> None:
    """Launch the graphical user interface."""
    setup_logging()
    load_from_args(argv)
    gui.main()


if __name__ == "__main__":
    main()
