"""Shared builders for test data."""

from __future__ import annotations

from singnote.domain.models import (
    ChordEvent,
    LyricSection,
    LyricSegment,
    MelodyNote,
    RhythmCue,
    Song,
    TeacherAnnotation,
)


def build_sample_song(song_id: str = "wish-you-were-here") -> Song:
    """Create a representative test song."""
    return Song(
        id=song_id,
        title="Wish You Were Here",
        artist="Pink Floyd",
        description="Seed song used for integration tests.",
        key_signature="G major",
        time_signature="4/4",
        tempo_bpm=61,
        tempo_notes="Relaxed half-time pulse.",
        strumming_pattern="D D U | D D U U",
        lyric_sections=[
            LyricSection(
                id="verse-1",
                title="Verse 1",
                order=0,
                segments=[
                    LyricSegment(id="seg-1", text="So", order=0),
                    LyricSegment(id="seg-2", text="you", order=1),
                    LyricSegment(id="seg-3", text="think", order=2),
                ],
            )
        ],
        chord_events=[
            ChordEvent(segment_id="seg-1", chord="C", position="before"),
            ChordEvent(segment_id="seg-3", chord="G", position="before"),
        ],
        melody_notes=[
            MelodyNote(
                segment_id="seg-1",
                note="E",
                octave=4,
                duration_beats=1.0,
            ),
            MelodyNote(
                segment_id="seg-2",
                note="G",
                octave=4,
                duration_beats=1.0,
            ),
        ],
        rhythm_cues=[
            RhythmCue(segment_id="seg-1", pattern="quarter"),
            RhythmCue(segment_id="seg-2", pattern="quarter"),
        ],
        teacher_annotations=[
            TeacherAnnotation(
                target_type="song",
                target_id=song_id,
                text="Support the vowel on the first phrase.",
            ),
            TeacherAnnotation(
                target_type="segment",
                target_id="seg-2",
                text="Lift the pitch slightly here.",
            ),
        ],
    )
