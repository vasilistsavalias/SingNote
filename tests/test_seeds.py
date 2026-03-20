"""Tests for initial seed content."""

from __future__ import annotations

import json
from pathlib import Path

from singnote.seeds import build_sample_songs
from tests.support import build_sample_song


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


def test_sample_seed_songs_can_load_from_json_directory(
    tmp_path: Path,
) -> None:
    """Seed loading should be data-driven rather than Python-song-specific."""
    song_path = tmp_path / "lesson-song.json"
    song_path.write_text(
        json.dumps(build_sample_song("lesson-song").model_dump(mode="json")),
        encoding="utf-8",
    )

    songs = build_sample_songs(tmp_path)

    assert len(songs) == 1
    assert songs[0].id == "lesson-song"
