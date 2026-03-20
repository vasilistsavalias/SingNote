"""Structured domain models for songs and musical annotations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LyricSegment(BaseModel):
    """A small lyric unit used as the alignment anchor for musical data."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    text: str = Field(min_length=1)
    order: int = Field(ge=0)


class LyricSection(BaseModel):
    """A song section such as verse or chorus."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    title: str | None = None
    order: int = Field(ge=0)
    segments: list[LyricSegment] = Field(default_factory=list)


class ChordEvent(BaseModel):
    """A chord annotation attached to a lyric segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    segment_id: str
    chord: str = Field(min_length=1)
    position: Literal["before", "after", "inline"] = "before"


class MelodyNote(BaseModel):
    """A melody note aligned to a lyric segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    segment_id: str
    note: str = Field(min_length=1)
    octave: int = Field(ge=0, le=8)
    duration_beats: float = Field(gt=0)


class RhythmCue(BaseModel):
    """A rhythm annotation aligned to a lyric segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    segment_id: str
    pattern: str = Field(min_length=1)
    emphasis: str | None = None


class TeacherAnnotation(BaseModel):
    """A free-form teacher note attached to a song, section, or segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    target_type: Literal["song", "section", "segment"]
    target_id: str
    text: str = Field(min_length=1)


class Song(BaseModel):
    """A fully structured song used by the practice workspace."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    title: str = Field(min_length=1)
    artist: str | None = None
    description: str | None = None
    lyric_sections: list[LyricSection] = Field(default_factory=list)
    chord_events: list[ChordEvent] = Field(default_factory=list)
    melody_notes: list[MelodyNote] = Field(default_factory=list)
    rhythm_cues: list[RhythmCue] = Field(default_factory=list)
    teacher_annotations: list[TeacherAnnotation] = Field(default_factory=list)

    @property
    def segment_ids(self) -> set[str]:
        """Return the lyric segment identifiers present in the song."""
        return {
            segment.id
            for section in self.lyric_sections
            for segment in section.segments
        }

    @property
    def section_ids(self) -> set[str]:
        """Return the lyric section identifiers present in the song."""
        return {section.id for section in self.lyric_sections}

    @model_validator(mode="after")
    def validate_alignment(self) -> Song:
        """Ensure aligned musical data points at existing lyric elements."""
        segment_ids = self.segment_ids
        if not segment_ids:
            raise ValueError("Song must include at least one lyric segment.")

        seen_segment_ids: set[str] = set()
        for section in self.lyric_sections:
            for segment in section.segments:
                if segment.id in seen_segment_ids:
                    raise ValueError(
                        f"Duplicate lyric segment id: {segment.id}"
                    )
                seen_segment_ids.add(segment.id)

        for event in self.chord_events:
            _validate_segment_reference(event.segment_id, segment_ids, "Chord")
        for note in self.melody_notes:
            _validate_segment_reference(
                note.segment_id, segment_ids, "Melody note"
            )
        for cue in self.rhythm_cues:
            _validate_segment_reference(
                cue.segment_id, segment_ids, "Rhythm cue"
            )
        for annotation in self.teacher_annotations:
            if annotation.target_type == "song":
                if annotation.target_id != self.id:
                    raise ValueError(
                        "Song-level annotations must target the song id."
                    )
                continue
            if annotation.target_type == "section":
                if annotation.target_id not in self.section_ids:
                    raise ValueError(
                        "Teacher annotation references an unknown section."
                    )
                continue
            _validate_segment_reference(
                annotation.target_id, segment_ids, "Teacher annotation"
            )
        return self


def _validate_segment_reference(
    segment_id: str, valid_segment_ids: set[str], label: str
) -> None:
    """Ensure a segment reference points at an existing lyric segment."""
    if segment_id not in valid_segment_ids:
        raise ValueError(f"{label} references unknown segment: {segment_id}")
