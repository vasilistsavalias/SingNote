"""Structured domain models for songs and musical annotations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MelodyNote(BaseModel):
    """A melody note aligned to a lyric segment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    segment_id: str
    note: str = Field(min_length=1)
    octave: int | None = Field(default=None, ge=0, le=8)
    duration_beats: float = Field(default=1.0, gt=0)
    order: int = Field(default=0, ge=0)

    @property
    def display_label(self) -> str:
        """Return the note as it should be shown in the UI."""
        return self.note if self.octave is None else f"{self.note}{self.octave}"


class MelodyPackage(BaseModel):
    """A grouped lyric chunk with its aligned melody-note sequence."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    text: str = Field(min_length=1)
    order: int = Field(default=0, ge=0)
    notes: list[MelodyNote] = Field(default_factory=list)


class LyricSegment(BaseModel):
    """A line-level lyric unit used as the alignment anchor for the app."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    text: str = Field(min_length=1)
    order: int = Field(ge=0)
    melody_packages: list[MelodyPackage] = Field(default_factory=list)


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
    roman_numeral: str | None = None
    order: int = Field(default=0, ge=0)
    position: Literal["before", "after", "inline"] = "before"


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
    key_signature: str | None = None
    time_signature: str | None = None
    tempo_bpm: int | None = Field(default=None, ge=1)
    tempo_notes: str | None = None
    strumming_pattern: str | None = None
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

        if not _song_has_any_melody_packages(self):
            for note in self.melody_notes:
                _validate_segment_reference(
                    note.segment_id,
                    segment_ids,
                    "Melody note",
                )
        _upgrade_legacy_melody_packages(self)
        _validate_melody_packages(self)
        if _song_has_any_melody_packages(self):
            self.melody_notes = _flatten_melody_packages(self)

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


def _song_has_any_melody_packages(song: Song) -> bool:
    """Return whether any lyric segment contains melody packages."""
    return any(
        segment.melody_packages
        for section in song.lyric_sections
        for segment in section.segments
    )


def _upgrade_legacy_melody_packages(song: Song) -> None:
    """Promote legacy flat melody notes into one fallback package per line."""
    if _song_has_any_melody_packages(song) or not song.melody_notes:
        return

    notes_by_segment: dict[str, list[MelodyNote]] = {}
    for note in song.melody_notes:
        notes_by_segment.setdefault(note.segment_id, []).append(note)

    for section in song.lyric_sections:
        for segment in section.segments:
            legacy_notes = sorted(
                notes_by_segment.get(segment.id, []),
                key=lambda note: note.order,
            )
            if not legacy_notes:
                continue
            segment.melody_packages = [
                MelodyPackage(
                    id=f"{segment.id}-pkg-1",
                    text=segment.text,
                    order=0,
                    notes=legacy_notes,
                )
            ]


def _validate_melody_packages(song: Song) -> None:
    """Validate package ids, note content, and segment ownership."""
    seen_package_ids: set[str] = set()
    for section in song.lyric_sections:
        for segment in section.segments:
            for package in segment.melody_packages:
                if package.id in seen_package_ids:
                    raise ValueError(
                        f"Duplicate melody package id: {package.id}"
                    )
                seen_package_ids.add(package.id)
                if not package.notes:
                    raise ValueError(
                        f"Melody package '{package.id}' must include notes."
                    )
                for note in package.notes:
                    if note.segment_id != segment.id:
                        raise ValueError(
                            "Melody package note segment ids must match "
                            "their parent lyric segment."
                        )


def _flatten_melody_packages(song: Song) -> list[MelodyNote]:
    """Derive the legacy flat note list from package-based melody data."""
    flattened: list[MelodyNote] = []
    for section in song.lyric_sections:
        for segment in section.segments:
            note_order = 0
            for package in sorted(
                segment.melody_packages, key=lambda package: package.order
            ):
                for package_note in sorted(
                    package.notes, key=lambda note: note.order
                ):
                    flattened.append(
                        MelodyNote(
                            segment_id=segment.id,
                            note=package_note.note,
                            octave=package_note.octave,
                            duration_beats=package_note.duration_beats,
                            order=note_order,
                        )
                    )
                    note_order += 1
    return flattened
