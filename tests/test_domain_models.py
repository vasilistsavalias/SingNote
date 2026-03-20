"""Tests for structured song domain validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from singnote.domain.models import MelodyNote, Song
from tests.support import build_sample_song


def test_song_rejects_duplicate_lyric_segment_ids() -> None:
    """Segments must be unique because they anchor all aligned data."""
    song = build_sample_song()
    song.lyric_sections[0].segments[1].id = "seg-1"

    with pytest.raises(ValidationError):
        Song.model_validate(song.model_dump())


def test_song_rejects_unknown_melody_alignment_target() -> None:
    """Melody notes must point to existing lyric segments."""
    song = build_sample_song()
    song.melody_notes.append(
        MelodyNote(
            segment_id="missing",
            note="A",
            octave=4,
            duration_beats=1.0,
        )
    )

    with pytest.raises(ValidationError):
        Song.model_validate(song.model_dump())


def test_song_exposes_section_and_segment_lookup_sets() -> None:
    """Alignment helpers should expose known sections and segments."""
    song = build_sample_song()

    assert song.section_ids == {"verse-1"}
    assert song.segment_ids == {"seg-1", "seg-2", "seg-3"}
