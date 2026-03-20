"""Streamlit entrypoint for SingNote."""

from singnote.bootstrap import bootstrap_application


def main() -> None:
    """Bootstrap and render the Streamlit application."""
    app = bootstrap_application()
    app.render()


if __name__ == "__main__":
    main()
