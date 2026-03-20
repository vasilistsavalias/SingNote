"""Tests for portable seed content."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from singnote.seeds import build_sample_songs


def test_sample_seed_song_is_complete_for_all_three_tabs() -> None:
    """The default seed should exercise harmony, melody, and rhythm."""
    songs = build_sample_songs()

    assert len(songs) == 1
    song = songs[0]
    assert song.title == "Wish You Were Here"
    assert song.chord_events
    assert song.melody_notes
    assert song.lyric_sections[0].segments[0].melody_packages
    assert song.rhythm_cues
    assert song.teacher_annotations


def test_sample_seed_songs_can_load_from_yaml_directory(
    tmp_path: Path,
) -> None:
    """Seed loading should support the package-authored YAML schema."""
    song_path = tmp_path / "lesson-song.yaml"
    song_path.write_text(
        "\n".join(
            [
                "song:",
                "  id: lesson-song",
                "  title: Lesson Song",
                "  tempo_bpm: 72",
                "sections:",
                "  - id: verse-1",
                "    title: Verse 1",
                "    lines:",
                "      - lyrics: First line",
                "        chords: [C, G]",
                "        roman_numerals: [I, V]",
                "        melody_packages:",
                "          - text: First",
                "            notes: [C4]",
                "          - text: line",
                "            notes:",
                "              - note: E4",
                "                beats: 2.0",
                "        rhythm:",
                "          pattern: quarters",
                "          emphasis: downbeat",
                "annotations:",
                "  - target_type: song",
                "    target_id: lesson-song",
                "    text: Teacher note",
            ]
        ),
        encoding="utf-8",
    )

    songs = build_sample_songs(tmp_path)

    assert len(songs) == 1
    assert songs[0].id == "lesson-song"
    assert songs[0].chord_events[1].roman_numeral == "V"
    assert songs[0].lyric_sections[0].segments[0].melody_packages[1].notes[
        0
    ].duration_beats == 2.0


def test_sample_seed_songs_can_load_legacy_json_melody_shape(
    tmp_path: Path,
) -> None:
    """Legacy JSON files should upgrade flat melody arrays to one package."""
    song_path = tmp_path / "legacy-song.json"
    song_path.write_text(
        json.dumps(
            {
                "song": {"id": "legacy-song", "title": "Legacy Song"},
                "sections": [
                    {
                        "id": "verse-1",
                        "title": "Verse 1",
                        "lines": [
                            {
                                "lyrics": "Legacy line",
                                "melody": ["C", "D"],
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    songs = build_sample_songs(tmp_path)

    assert len(songs) == 1
    assert songs[0].lyric_sections[0].segments[0].melody_packages[0].text == (
        "Legacy line"
    )
    assert songs[0].melody_notes[1].note == "D"


def test_portable_payload_rejects_empty_package_notes(tmp_path: Path) -> None:
    """Package auth should fail fast when a package has no notes."""
    song_path = tmp_path / "bad-song.yaml"
    song_path.write_text(
        "\n".join(
            [
                "song:",
                "  id: bad-song",
                "  title: Bad Song",
                "sections:",
                "  - id: verse-1",
                "    lines:",
                "      - lyrics: Broken",
                "        melody_packages:",
                "          - text: Bro",
                "            notes: []",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        build_sample_songs(tmp_path)
