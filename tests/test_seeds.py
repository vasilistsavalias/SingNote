"""Tests for portable seed content."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from singnote.seeds import build_sample_songs, song_from_portable_text


def test_sample_seed_song_is_complete_for_all_three_tabs() -> None:
    """The default seed should exercise harmony, melody, and rhythm."""
    songs = build_sample_songs()
    song_lookup = {song.id: song for song in songs}

    assert "wish-you-were-here" in song_lookup
    song = song_lookup["wish-you-were-here"]
    assert song.title == "Wish You Were Here"
    assert song.chord_events
    assert song.melody_notes
    assert song.lyric_sections[0].segments[0].melody_packages
    assert song.rhythm_cues
    assert song.teacher_annotations


def test_kakes_synitheies_seed_uses_greekrocker_chord_skeleton() -> None:
    """The Greek seed should load as a practice-ready chord chart."""
    songs = build_sample_songs()
    song = {song.id: song for song in songs}["kakes-synitheies"]

    assert song.title == "Κακές Συνήθειες"
    assert song.artist == "Μίλτος Πασχαλίδης"
    assert song.key_signature == "G major"
    assert [section.id for section in song.lyric_sections] == [
        "intro",
        "verse-1",
        "chorus-1",
        "interlude",
        "verse-2",
        "chorus-2",
        "outro",
    ]
    assert song.lyric_sections[0].segments[0].text == "G Gsus4 G Gsus4"
    first_line_chords = [
        event.chord
        for event in song.chord_events
        if event.segment_id == "verse-1-1"
    ]
    assert first_line_chords == ["G", "Am", "C", "D", "G"]
    refrain_turn = [
        event.chord
        for event in song.chord_events
        if event.segment_id == "chorus-1-2"
    ]
    assert refrain_turn == ["Am", "D", "B7", "Em"]


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


def test_portable_yaml_accepts_melody_text_shorthand() -> None:
    """Portable YAML should support 'text = notes' melody shorthand."""
    song = song_from_portable_text(
        "\n".join(
            [
                "song:",
                "  id: shorthand-song",
                "  title: Shorthand Song",
                "sections:",
                "  - id: verse-1",
                "    lines:",
                "      - lyrics: So, so you think you can tell,",
                "        melody_text: |",
                "          So = C,B,G",
                "          So => C",
                "          you = B",
            ]
        )
    )

    packages = song.lyric_sections[0].segments[0].melody_packages
    assert [package.text for package in packages] == ["So", "So", "you"]
    assert [note.note for note in packages[0].notes] == ["C", "B", "G"]
    assert packages[1].notes[0].note == "C"


def test_portable_yaml_rejects_invalid_melody_text_shorthand() -> None:
    """Shorthand melody lines should fail fast when the separator is missing."""
    with pytest.raises(ValueError):
        song_from_portable_text(
            "\n".join(
                [
                    "song:",
                    "  id: bad-shorthand-song",
                    "  title: Bad Shorthand Song",
                    "sections:",
                    "  - id: verse-1",
                    "    lines:",
                    "      - lyrics: Broken",
                    "        melody_text: |",
                    "          So C,B,G",
                ]
            )
        )


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
