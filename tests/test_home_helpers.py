"""Tests for home-page helper behavior."""

from __future__ import annotations

import pytest

from singnote.ui.home import (
    _apply_melody_update,
    _melody_note_payload,
    _parse_note_token,
)
from tests.support import build_sample_song


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


def test_melody_note_payload_includes_lyric_context() -> None:
    """The long-press component should receive note labels and lyric text."""
    payload = _melody_note_payload(build_sample_song())

    assert payload[0]["segment_id"] == "seg-1"
    assert payload[0]["note_label"] == "E4"
    assert payload[0]["lyric"] == "So"


def test_apply_melody_update_replaces_the_target_note() -> None:
    """A long-press note edit should update the matching melody note."""
    song = build_sample_song()

    _apply_melody_update(
        song,
        {
            "segment_id": "seg-2",
            "order": 0,
            "note_label": "A4",
            "duration_beats": 1.5,
        },
    )

    updated_note = next(
        note for note in song.melody_notes if note.segment_id == "seg-2"
    )
    assert updated_note.note == "A"
    assert updated_note.octave == 4
    assert updated_note.duration_beats == 1.5


def test_apply_melody_update_rejects_unknown_segment_ids() -> None:
    """Inline note updates should fail for missing segment ids."""
    song = build_sample_song()

    with pytest.raises(ValueError):
        _apply_melody_update(
            song,
            {
                "segment_id": "missing",
                "order": 0,
                "note_label": "A4",
                "duration_beats": 1.0,
            },
        )
