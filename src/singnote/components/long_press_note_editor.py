"""Long-press melody note editor component."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).with_name("long_press_note_editor_frontend")
_COMPONENT = components.declare_component(
    "long_press_note_editor",
    path=str(_FRONTEND_DIR),
)


def long_press_note_editor(
    notes: list[dict[str, Any]],
    key: str,
) -> dict[str, Any] | None:
    """Render the long-press note editor and return saved note updates."""
    result = _COMPONENT(notes=notes, key=key, default=None)
    return cast(dict[str, Any] | None, result)
