"""Entrypoint for running Hermes as a module."""

from .ui import gui


def main(argv: list[str] | None = None) -> None:
    """Launch the graphical user interface."""
    gui.main(argv)


if __name__ == "__main__":
    main()
