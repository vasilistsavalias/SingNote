"""Tests for initial seed content."""

from __future__ import annotations

import json
from pathlib import Path

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


def test_sample_seed_songs_can_load_from_json_directory(
    tmp_path: Path,
) -> None:
    """Seed loading should support the line-based authored JSON schema."""
    song_path = tmp_path / "lesson-song.json"
    song_path.write_text(
        json.dumps(
            {
                "song": {
                    "id": "lesson-song",
                    "title": "Lesson Song",
                    "tempo_bpm": 72,
                },
                "sections": [
                    {
                        "id": "verse-1",
                        "title": "Verse 1",
                        "lines": [
                            {
                                "lyrics": "First line",
                                "chords": ["C", "G"],
                                "roman_numerals": ["I", "V"],
                                "melody": [
                                    "C4",
                                    {"note": "E4", "beats": 2.0},
                                ],
                                "rhythm": {
                                    "pattern": "quarters",
                                    "emphasis": "downbeat",
                                },
                            }
                        ],
                    }
                ],
                "annotations": [
                    {
                        "target_type": "song",
                        "target_id": "lesson-song",
                        "text": "Teacher note",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    songs = build_sample_songs(tmp_path)

    assert len(songs) == 1
    assert songs[0].id == "lesson-song"
    assert songs[0].chord_events[1].roman_numeral == "V"
    assert songs[0].melody_notes[1].duration_beats == 2.0
