"""Entrypoint for running Hermes as a module."""

from .ui import gui


def main() -> None:
    """Launch the graphical user interface."""
    gui.main()


if __name__ == "__main__":
    main()
