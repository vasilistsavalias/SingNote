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
    song.lyric_sections[0].segments[0].melody_packages = []
    song.lyric_sections[0].segments[1].melody_packages = []
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


def test_song_rejects_package_notes_with_mismatched_segment_ids() -> None:
    """Package notes must belong to the lyric segment that owns them."""
    song = build_sample_song()
    first_package_note = (
        song.lyric_sections[0].segments[0].melody_packages[0].notes[0]
    )
    first_package_note.segment_id = "seg-2"

    with pytest.raises(ValidationError):
        Song.model_validate(song.model_dump())


def test_song_upgrades_legacy_flat_notes_to_one_fallback_package() -> None:
    """Legacy songs should still load by creating one fallback package."""
    song = build_sample_song()
    song.lyric_sections[0].segments[0].melody_packages = []
    song.lyric_sections[0].segments[1].melody_packages = []
    song.melody_notes = [
        MelodyNote(segment_id="seg-1", note="C", duration_beats=1.0, order=0),
        MelodyNote(segment_id="seg-1", note="B", duration_beats=1.0, order=1),
    ]

    validated = Song.model_validate(song.model_dump())

    packages = validated.lyric_sections[0].segments[0].melody_packages
    assert len(packages) == 1
    assert packages[0].text == "So you think"
    assert packages[0].notes[1].note == "B"


def test_song_exposes_section_and_segment_lookup_sets() -> None:
    """Alignment helpers should expose known sections and segments."""
    song = build_sample_song()

    assert song.section_ids == {"verse-1"}
    assert song.segment_ids == {"seg-1", "seg-2"}
