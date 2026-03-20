"""JSON-backed seed song loading for SingNote."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast

from singnote.domain.models import (
    ChordEvent,
    LyricSection,
    LyricSegment,
    MelodyNote,
    RhythmCue,
    Song,
    TeacherAnnotation,
)

SEED_SONGS_DIR = Path(__file__).resolve().parents[2] / "seed_data" / "songs"


def build_sample_songs(seed_songs_dir: Path | None = None) -> list[Song]:
    """Load seed songs from JSON files."""
    songs_dir = seed_songs_dir or SEED_SONGS_DIR
    if not songs_dir.exists():
        return []

    return [_load_song_file(path) for path in sorted(songs_dir.glob("*.json"))]


def _load_song_file(path: Path) -> Song:
    """Load one seed song file into a validated domain model."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Seed file '{path.name}' must contain a JSON object.")

    if "lyric_sections" in payload:
        return Song.model_validate(payload)

    return _song_from_authored_payload(payload)


def _song_from_authored_payload(payload: dict[str, Any]) -> Song:
    """Build a song from the human-authored line-based seed schema."""
    raw_song = _as_dict(payload.get("song", payload), "song")
    section_models, chord_events, melody_notes, rhythm_cues = _parse_sections(
        payload
    )
    annotations = _parse_annotations(payload)

    return Song(
        id=_required_str(raw_song, "id"),
        title=_required_str(raw_song, "title"),
        artist=_optional_str(raw_song.get("artist")),
        description=_optional_str(raw_song.get("description")),
        key_signature=_optional_str(raw_song.get("key_signature")),
        time_signature=_optional_str(raw_song.get("time_signature")),
        tempo_bpm=_optional_int(raw_song.get("tempo_bpm"), "tempo_bpm"),
        tempo_notes=_optional_str(raw_song.get("tempo_notes")),
        strumming_pattern=_optional_str(raw_song.get("strumming_pattern")),
        lyric_sections=section_models,
        chord_events=chord_events,
        melody_notes=melody_notes,
        rhythm_cues=rhythm_cues,
        teacher_annotations=annotations,
    )


def _parse_sections(
    payload: Mapping[str, Any],
) -> tuple[
    list[LyricSection], list[ChordEvent], list[MelodyNote], list[RhythmCue]
]:
    section_models: list[LyricSection] = []
    chord_events: list[ChordEvent] = []
    melody_notes: list[MelodyNote] = []
    rhythm_cues: list[RhythmCue] = []

    for section_order, raw_section in enumerate(
        _as_list(payload.get("sections"), "sections")
    ):
        section = _as_dict(raw_section, f"sections[{section_order}]")
        section_id = _required_str(section, "id")
        section_title = _optional_str(section.get("title"))
        segments: list[LyricSegment] = []

        for line_order, raw_line in enumerate(
            _as_list(section.get("lines"), f"sections[{section_order}].lines")
        ):
            line = _as_dict(
                raw_line,
                f"sections[{section_order}].lines[{line_order}]",
            )
            segment_id = _optional_str(line.get("id")) or (
                f"{section_id}-{line_order + 1}"
            )
            segments.append(
                LyricSegment(
                    id=segment_id,
                    text=_required_str(line, "lyrics"),
                    order=line_order,
                )
            )
            chord_events.extend(_parse_chords(line, segment_id))
            melody_notes.extend(_parse_melody(line, segment_id))
            rhythm_cue = _parse_rhythm(line, segment_id)
            if rhythm_cue is not None:
                rhythm_cues.append(rhythm_cue)

        section_models.append(
            LyricSection(
                id=section_id,
                title=section_title,
                order=section_order,
                segments=segments,
            )
        )

    return section_models, chord_events, melody_notes, rhythm_cues


def _parse_chords(
    line: Mapping[str, Any], segment_id: str
) -> list[ChordEvent]:
    events: list[ChordEvent] = []
    raw_chords = _as_list(line.get("chords", []), "chords")
    raw_roman_numerals = line.get("roman_numerals", [])
    roman_numerals = _as_list(raw_roman_numerals, "roman_numerals")

    for order, raw_chord in enumerate(raw_chords):
        chord_symbol: str
        roman_numeral: str | None = None
        position: Literal["before", "after", "inline"] = "before"

        if isinstance(raw_chord, str):
            chord_symbol = raw_chord.strip()
            roman_numeral = _optional_list_item(roman_numerals, order)
        else:
            chord_data = _as_dict(raw_chord, f"chords[{order}]")
            chord_symbol = _required_str(chord_data, "symbol")
            roman_numeral = _optional_str(chord_data.get("roman_numeral"))
            position_value = (
                _optional_str(chord_data.get("position")) or "before"
            )
            position = cast(
                Literal["before", "after", "inline"], position_value
            )

        events.append(
            ChordEvent(
                segment_id=segment_id,
                chord=chord_symbol,
                roman_numeral=roman_numeral,
                order=order,
                position=position,
            )
        )

    return events


def _parse_melody(
    line: Mapping[str, Any], segment_id: str
) -> list[MelodyNote]:
    notes: list[MelodyNote] = []
    raw_melody = _as_list(line.get("melody", []), "melody")
    for order, raw_note in enumerate(raw_melody):
        if isinstance(raw_note, str):
            note, octave = _split_note_token(raw_note)
            duration_beats = 1.0
        else:
            note_data = _as_dict(raw_note, f"melody[{order}]")
            note, octave = _split_note_token(_required_str(note_data, "note"))
            duration_beats = float(note_data.get("beats", 1.0))

        notes.append(
            MelodyNote(
                segment_id=segment_id,
                note=note,
                octave=octave,
                duration_beats=duration_beats,
                order=order,
            )
        )

    return notes


def _parse_rhythm(
    line: Mapping[str, Any], segment_id: str
) -> RhythmCue | None:
    raw_rhythm = line.get("rhythm")
    if raw_rhythm is None:
        return None
    if isinstance(raw_rhythm, str):
        return RhythmCue(segment_id=segment_id, pattern=raw_rhythm)

    rhythm = _as_dict(raw_rhythm, "rhythm")
    return RhythmCue(
        segment_id=segment_id,
        pattern=_required_str(rhythm, "pattern"),
        emphasis=_optional_str(rhythm.get("emphasis")),
    )


def _parse_annotations(payload: Mapping[str, Any]) -> list[TeacherAnnotation]:
    raw_annotations = _as_list(payload.get("annotations", []), "annotations")
    return [
        TeacherAnnotation.model_validate(
            _as_dict(annotation, f"annotations[{index}]")
        )
        for index, annotation in enumerate(raw_annotations)
    ]


def _split_note_token(token: str) -> tuple[str, int | None]:
    match = re.fullmatch(r"([A-Ga-g][#b]?)(\d)?", token.strip())
    if match is None:
        raise ValueError(
            f"Invalid melody note '{token}'. Use formats like C, Bb, or C4."
        )
    note = match.group(1).upper()
    octave = int(match.group(2)) if match.group(2) else None
    return note, octave


def _as_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def _as_list(value: Any, label: str) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    raise ValueError(f"{label} must be a JSON array.")


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = _optional_str(data.get(key))
    if value is None:
        raise ValueError(f"Missing required string field '{key}'.")
    return value


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected a string value.")
    stripped = value.strip()
    return stripped or None


def _optional_int(value: Any, key: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Field '{key}' must be an integer.")
    return int(value)


def _optional_list_item(values: list[Any], index: int) -> str | None:
    if index >= len(values):
        return None
    value = values[index]
    return _optional_str(value)
