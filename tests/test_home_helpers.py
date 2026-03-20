"""Tests for home-page helper behavior."""

from __future__ import annotations

import pytest

from singnote.ui.home import _parse_note_token


def test_parse_note_token_accepts_sharp_notes() -> None:
    """Inline note edits should accept note tokens like F#4."""
    note = _parse_note_token("seg-1", "F#4", 1.5)

    assert note.segment_id == "seg-1"
    assert note.note == "F#"
    assert note.octave == 4
    assert note.duration_beats == 1.5


def test_parse_note_token_rejects_invalid_tokens() -> None:
    """Inline note edits should reject malformed note labels."""
    with pytest.raises(ValueError):
        _parse_note_token("seg-1", "middle-c", 1.0)
