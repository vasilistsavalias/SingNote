"""Helpers for the authoring workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, cast

from singnote.domain.models import (
    ChordEvent,
    LyricSection,
    LyricSegment,
    MelodyNote,
    RhythmCue,
    Song,
    TeacherAnnotation,
)
from singnote.seeds import song_from_portable_text, song_to_portable_text


@dataclass(frozen=True)
class SongEditorValues:
    """Editable text values used by the MVP authoring form."""

    song_id: str
    title: str
    artist: str
    description: str
    key_signature: str
    time_signature: str
    tempo_bpm: str
    tempo_notes: str
    strumming_pattern: str
    lyrics_text: str
    chords_text: str
    melody_text: str
    rhythm_text: str
    annotations_text: str


def build_song_from_editor_values(values: SongEditorValues) -> Song:
    """Convert form text areas into a validated song model."""
    lyric_sections = _parse_lyrics(values.lyrics_text)
    song = Song(
        id=_normalize_song_id(values.song_id or values.title),
        title=values.title.strip(),
        artist=_optional_text(values.artist),
        description=_optional_text(values.description),
        key_signature=_optional_text(values.key_signature),
        time_signature=_optional_text(values.time_signature),
        tempo_bpm=_optional_int(values.tempo_bpm, "Tempo"),
        tempo_notes=_optional_text(values.tempo_notes),
        strumming_pattern=_optional_text(values.strumming_pattern),
        lyric_sections=lyric_sections,
        chord_events=_parse_chords(values.chords_text),
        melody_notes=_parse_melody(values.melody_text),
        rhythm_cues=_parse_rhythm(values.rhythm_text),
        teacher_annotations=_parse_annotations(
            values.annotations_text,
            _normalize_song_id(values.song_id or values.title),
        ),
    )
    return song


def build_song_from_yaml_text(yaml_text: str) -> Song:
    """Convert portable song YAML text into a validated song model."""
    return song_from_portable_text(yaml_text)


def yaml_text_from_song(song: Song) -> str:
    """Serialize a song into portable YAML for external editing."""
    return song_to_portable_text(song)


def editor_values_from_song(song: Song) -> SongEditorValues:
    """Serialize a song into editable text areas."""
    lyric_lines = []
    for section in song.lyric_sections:
        lyric_lines.append(f"[{section.title or section.id}]")
        lyric_lines.append(
            " ".join(segment.text for segment in section.segments)
        )
        lyric_lines.append("")
    lyrics_text = "\n".join(lyric_lines).strip()

    chords_text = "\n".join(
        "|".join(
            part
            for part in [
                event.segment_id,
                event.chord,
                event.roman_numeral or "",
                event.position,
            ]
            if part != ""
        )
        for event in song.chord_events
    )
    melody_text = "\n".join(
        f"{note.segment_id}|{note.display_label}|{note.duration_beats:g}"
        for note in song.melody_notes
    )
    rhythm_text = "\n".join(
        f"{cue.segment_id}|{cue.pattern}|{cue.emphasis or ''}".rstrip("|")
        for cue in song.rhythm_cues
    )
    annotations_text = "\n".join(
        f"{annotation.target_type}|{annotation.target_id}|{annotation.text}"
        for annotation in song.teacher_annotations
    )

    return SongEditorValues(
        song_id=song.id,
        title=song.title,
        artist=song.artist or "",
        description=song.description or "",
        key_signature=song.key_signature or "",
        time_signature=song.time_signature or "",
        tempo_bpm="" if song.tempo_bpm is None else str(song.tempo_bpm),
        tempo_notes=song.tempo_notes or "",
        strumming_pattern=song.strumming_pattern or "",
        lyrics_text=lyrics_text,
        chords_text=chords_text,
        melody_text=melody_text,
        rhythm_text=rhythm_text,
        annotations_text=annotations_text,
    )


def blank_editor_values() -> SongEditorValues:
    """Return empty defaults for creating a new song."""
    return SongEditorValues(
        song_id="",
        title="",
        artist="",
        description="",
        key_signature="",
        time_signature="4/4",
        tempo_bpm="60",
        tempo_notes="Relaxed half-time feel",
        strumming_pattern="D D U | D D U U",
        lyrics_text="[Verse 1]\nType lyrics here",
        chords_text="seg-1|C|before",
        melody_text="seg-1|C4|1",
        rhythm_text="seg-1|quarter|downbeat",
        annotations_text="song|new-song|Add a coaching note",
    )


def _parse_lyrics(lyrics_text: str) -> list[LyricSection]:
    sections: list[LyricSection] = []
    current_title = "Section 1"
    current_lines: list[str] = []

    for raw_line in lyrics_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_lines:
                sections.append(
                    _build_section(current_title, current_lines, len(sections))
                )
                current_lines = []
            current_title = line[1:-1].strip() or f"Section {len(sections) + 1}"
            continue
        current_lines.append(line)

    if current_lines:
        sections.append(
            _build_section(current_title, current_lines, len(sections))
        )

    return sections


def _build_section(
    title: str,
    lines: list[str],
    section_order: int,
) -> LyricSection:
    segments: list[LyricSegment] = []
    section_slug = _slugify(title)
    for segment_order, line in enumerate(lines):
        segments.append(
            LyricSegment(
                id=f"{section_slug}-{segment_order + 1}",
                text=line,
                order=segment_order,
            )
        )

    return LyricSection(
        id=section_slug,
        title=title,
        order=section_order,
        segments=segments,
    )


def _parse_chords(chords_text: str) -> list[ChordEvent]:
    events: list[ChordEvent] = []
    for index, line in enumerate(_iter_non_empty_lines(chords_text)):
        segment_id, chord, *rest = _split_pipe_line(line, 2)
        roman_numeral: str | None = None
        position: Literal["before", "after", "inline"] = "before"
        if len(rest) == 1:
            if rest[0] in {"before", "after", "inline"}:
                position = cast(Literal["before", "after", "inline"], rest[0])
            else:
                roman_numeral = rest[0]
        elif len(rest) >= 2:
            roman_numeral = rest[0] or None
            position = cast(Literal["before", "after", "inline"], rest[1])
        events.append(
            ChordEvent(
                segment_id=segment_id,
                chord=chord,
                roman_numeral=roman_numeral,
                order=index,
                position=position,
            )
        )
    return events


def _parse_melody(melody_text: str) -> list[MelodyNote]:
    notes: list[MelodyNote] = []
    for index, line in enumerate(_iter_non_empty_lines(melody_text)):
        segment_id, note_token, duration = _split_pipe_line(line, 3)
        match = re.fullmatch(r"([A-Ga-g][#b]?)(\d)?", note_token.strip())
        if match is None:
            raise ValueError(
                "Invalid melody note format "
                f"'{note_token}'. Use forms like C or C4."
            )
        notes.append(
            MelodyNote(
                segment_id=segment_id,
                note=match.group(1).upper(),
                octave=int(match.group(2)) if match.group(2) else None,
                duration_beats=float(duration),
                order=index,
            )
        )
    return notes


def _parse_rhythm(rhythm_text: str) -> list[RhythmCue]:
    cues: list[RhythmCue] = []
    for line in _iter_non_empty_lines(rhythm_text):
        parts = line.split("|")
        if len(parts) < 2:
            raise ValueError(
                f"Invalid rhythm line '{line}'. Use segment|pattern|emphasis."
            )
        segment_id = parts[0].strip()
        pattern = parts[1].strip()
        emphasis = parts[2].strip() if len(parts) > 2 else None
        cues.append(
            RhythmCue(
                segment_id=segment_id,
                pattern=pattern,
                emphasis=emphasis or None,
            )
        )
    return cues


def _parse_annotations(
    annotations_text: str,
    fallback_song_id: str,
) -> list[TeacherAnnotation]:
    annotations: list[TeacherAnnotation] = []
    for line in _iter_non_empty_lines(annotations_text):
        target_type, target_id, text = _split_pipe_line(line, 3)
        if target_type == "song" and target_id == "new-song":
            target_id = fallback_song_id
        target_type = cast(
            Literal["song", "section", "segment"],
            target_type,
        )
        annotations.append(
            TeacherAnnotation(
                target_type=target_type,
                target_id=target_id,
                text=text,
            )
        )
    return annotations


def _iter_non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _split_pipe_line(line: str, required_parts: int) -> list[str]:
    parts = [part.strip() for part in line.split("|")]
    if len(parts) < required_parts:
        raise ValueError(
            "Invalid structured line "
            f"'{line}'. Expected {required_parts} parts."
        )
    return parts


def _normalize_song_id(value: str) -> str:
    normalized = _slugify(value)
    if not normalized:
        raise ValueError("Song id or title must contain usable characters.")
    return normalized


def _optional_text(value: str) -> str | None:
    stripped = value.strip()
    return stripped or None


def _optional_int(value: str, label: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError as error:
        raise ValueError(f"{label} must be a whole number.") from error


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")
