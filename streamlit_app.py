"""Streamlit entrypoint for SingNote."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> None:
    """Bootstrap and render the Streamlit application."""
    from singnote.bootstrap import bootstrap_application

    app = bootstrap_application()
    app.render()


if __name__ == "__main__":
    main()
