"""Tests for home-page helper behavior."""

from __future__ import annotations

import pytest

from singnote.ui.home import (
    _apply_melody_line_update,
    _format_melody_note_sequence,
    _lyrics_sheet_markup,
    _parse_note_sequence,
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


def test_format_melody_note_sequence_is_readable() -> None:
    """Melody lines should render as one readable note string."""
    melody_notes = build_sample_song().melody_notes

    assert _format_melody_note_sequence(melody_notes) == "E4 G4"


def test_parse_note_sequence_accepts_commas_and_spaces() -> None:
    """Line editing should accept either comma- or space-separated notes."""
    notes = _parse_note_sequence("C, B G, A")

    assert notes == ["C", "B", "G", "A"]


def test_apply_melody_line_update_replaces_lyric_and_notes() -> None:
    """A line edit should update both lyric text and melody notes."""
    song = build_sample_song()

    _apply_melody_line_update(
        song,
        segment_id="seg-2",
        lyric_text="youuu",
        notes_text="A4 C5",
    )

    updated_notes = [
        note for note in song.melody_notes if note.segment_id == "seg-2"
    ]
    assert len(updated_notes) == 2
    assert updated_notes[0].note == "A"
    assert updated_notes[0].octave == 4
    assert updated_notes[0].duration_beats == 1.0
    assert updated_notes[1].note == "C"
    assert updated_notes[1].octave == 5
    assert song.lyric_sections[0].segments[1].text == "youuu"


def test_apply_melody_line_update_rejects_unknown_segment_ids() -> None:
    """Line updates should fail for missing segment ids."""
    song = build_sample_song()

    with pytest.raises(ValueError):
        _apply_melody_line_update(
            song,
            segment_id="missing",
            lyric_text="missing",
            notes_text="A4",
        )


def test_lyrics_sheet_markup_reads_like_one_chart() -> None:
    """Lyrics tab markup should render as one coherent song sheet."""
    markup = _lyrics_sheet_markup(build_sample_song())

    assert 'class="sn-song-sheet"' in markup
    assert 'class="sn-sheet-section-title"' in markup
    assert 'class="sn-sheet-chords"' in markup
    assert 'class="sn-sheet-lyric"' in markup
