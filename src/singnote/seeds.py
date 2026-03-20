"""Sample seed content for the SingNote MVP."""

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


def build_sample_songs() -> list[Song]:
    """Return the default seed songs for a fresh SingNote instance."""
    return [
        Song(
            id="wish-you-were-here",
            title="Wish You Were Here",
            artist="Pink Floyd",
            description=(
                "Sample lesson song with lyrics, chords, melody, and rhythm "
                "annotations."
            ),
            lyric_sections=[
                LyricSection(
                    id="verse-1",
                    title="Verse 1",
                    order=0,
                    segments=[
                        LyricSegment(id="seg-1", text="So", order=0),
                        LyricSegment(id="seg-2", text="so", order=1),
                        LyricSegment(id="seg-3", text="you", order=2),
                        LyricSegment(id="seg-4", text="think", order=3),
                        LyricSegment(id="seg-5", text="you", order=4),
                        LyricSegment(id="seg-6", text="can", order=5),
                        LyricSegment(id="seg-7", text="tell", order=6),
                    ],
                )
            ],
            chord_events=[
                ChordEvent(segment_id="seg-1", chord="G", position="before"),
                ChordEvent(segment_id="seg-3", chord="C", position="before"),
                ChordEvent(segment_id="seg-5", chord="D", position="before"),
            ],
            melody_notes=[
                MelodyNote(
                    segment_id="seg-1",
                    note="D",
                    octave=4,
                    duration_beats=1.0,
                ),
                MelodyNote(
                    segment_id="seg-2",
                    note="E",
                    octave=4,
                    duration_beats=1.0,
                ),
                MelodyNote(
                    segment_id="seg-3",
                    note="G",
                    octave=4,
                    duration_beats=1.0,
                ),
                MelodyNote(
                    segment_id="seg-4",
                    note="A",
                    octave=4,
                    duration_beats=1.0,
                ),
            ],
            rhythm_cues=[
                RhythmCue(
                    segment_id="seg-1",
                    pattern="quarter",
                    emphasis="downbeat",
                ),
                RhythmCue(segment_id="seg-2", pattern="quarter"),
                RhythmCue(segment_id="seg-3", pattern="quarter"),
                RhythmCue(segment_id="seg-4", pattern="quarter"),
            ],
            teacher_annotations=[
                TeacherAnnotation(
                    target_type="song",
                    target_id="wish-you-were-here",
                    text="Keep the opening phrase relaxed and supported.",
                ),
                TeacherAnnotation(
                    target_type="segment",
                    target_id="seg-4",
                    text="Do not press the word 'think'.",
                ),
            ],
        )
    ]
