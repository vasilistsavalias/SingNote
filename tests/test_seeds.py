"""Tests for initial seed content."""

from __future__ import annotations

from singnote.seeds import build_sample_songs


def test_sample_seed_song_is_complete_for_all_three_tabs() -> None:
    """The default seed should exercise harmony, melody, and rhythm."""
    songs = build_sample_songs()

    assert len(songs) == 1
    song = songs[0]
    assert song.title == "Wish You Were Here"
    assert song.chord_events
    assert song.melody_notes
    assert song.rhythm_cues
    assert song.teacher_annotations
