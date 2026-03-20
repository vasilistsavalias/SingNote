"""Tests for authoring form parsing and serialization."""

from __future__ import annotations

import pytest

from singnote.ui.authoring import (
    SongEditorValues,
    build_song_from_editor_values,
    build_song_from_yaml_text,
    editor_values_from_song,
    yaml_text_from_song,
)
from tests.support import build_sample_song


def test_build_song_from_editor_values_maps_structured_text_to_song() -> None:
    """The authoring form should map text areas into structured song data."""
    values = SongEditorValues(
        song_id="",
        title="Lesson Song",
        artist="Teacher",
        description="Warmup exercise",
        key_signature="C major",
        time_signature="4/4",
        tempo_bpm="72",
        tempo_notes="Keep it grounded",
        strumming_pattern="D D U U",
        lyrics_text="[Verse 1]\nHello bright world\nGoodbye moon",
        chords_text="verse-1-1|C|before\nverse-1-2|G|before",
        melody_text="verse-1-1|C4|1\nverse-1-2|D4|1",
        rhythm_text="verse-1-1|quarter|downbeat",
        annotations_text="song|new-song|Start with breath support",
    )

    song = build_song_from_editor_values(values)

    assert song.id == "lesson-song"
    assert song.key_signature == "C major"
    assert song.tempo_bpm == 72
    assert song.lyric_sections[0].segments[0].id == "verse-1-1"
    assert song.lyric_sections[0].segments[0].text == "Hello bright world"
    assert song.chord_events[1].segment_id == "verse-1-2"
    assert song.melody_notes[1].note == "D"
    assert song.teacher_annotations[0].target_id == "lesson-song"


def test_build_song_from_editor_values_rejects_bad_melody_tokens() -> None:
    """Melody note syntax should be explicit and validated."""
    values = SongEditorValues(
        song_id="bad-song",
        title="Bad Song",
        artist="",
        description="",
        key_signature="",
        time_signature="4/4",
        tempo_bpm="60",
        tempo_notes="",
        strumming_pattern="",
        lyrics_text="[Verse 1]\nHello",
        chords_text="verse-1-1|C|before",
        melody_text="verse-1-1|middle-c|1",
        rhythm_text="verse-1-1|quarter",
        annotations_text="song|bad-song|Note issue",
    )

    with pytest.raises(ValueError):
        build_song_from_editor_values(values)


def test_editor_values_from_song_round_trips_existing_song() -> None:
    """Editing an existing song should expose structured defaults."""
    values = editor_values_from_song(build_sample_song())

    assert values.song_id == "wish-you-were-here"
    assert "[Verse 1]" in values.lyrics_text
    assert values.key_signature == build_sample_song().key_signature
    assert "seg-1|C|before" in values.chords_text
    assert "seg-1|E4|1" in values.melody_text


def test_build_song_from_yaml_text_supports_package_authored_songs() -> None:
    """Portable YAML should preserve melody package groupings."""
    song = build_song_from_yaml_text(
        """
        song:
          id: yaml-song
          title: YAML Song
        sections:
          - id: verse-1
            title: Verse 1
            lines:
              - lyrics: So, so you think you can tell,
                melody_packages:
                  - text: So
                    notes: [C, B, G]
                  - text: so you think you can tell
                    notes: [C, B, C, B, G, A]
        annotations: []
        """
    )

    packages = song.lyric_sections[0].segments[0].melody_packages
    assert song.id == "yaml-song"
    assert len(packages) == 2
    assert packages[0].text == "So"
    assert packages[1].notes[5].note == "A"


def test_yaml_text_from_song_exposes_package_authored_shape() -> None:
    """Portable YAML export should include grouped melody packages."""
    yaml_text = yaml_text_from_song(build_sample_song())

    assert "melody_packages:" in yaml_text
    assert "text: So" in yaml_text
