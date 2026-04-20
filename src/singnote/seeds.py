"""Portable song loading and serialization helpers for SingNote."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from singnote.domain.models import (
    ChordEvent,
    LyricSection,
    LyricSegment,
    MelodyNote,
    MelodyPackage,
    RhythmCue,
    Song,
    TeacherAnnotation,
)

SEED_SONGS_DIR = Path(__file__).resolve().parents[2] / "seed_data" / "songs"


def build_sample_songs(seed_songs_dir: Path | None = None) -> list[Song]:
    """Load seed songs from YAML or JSON files."""
    songs_dir = seed_songs_dir or SEED_SONGS_DIR
    if not songs_dir.exists():
        return []

    paths = sorted(
        [
            *songs_dir.glob("*.yaml"),
            *songs_dir.glob("*.yml"),
            *songs_dir.glob("*.json"),
        ]
    )
    return [_load_song_file(path) for path in paths]


def song_from_portable_text(payload_text: str) -> Song:
    """Parse portable YAML or JSON text into a validated song."""
    payload = yaml.safe_load(payload_text)
    if not isinstance(payload, dict):
        raise ValueError("Song text must contain a YAML or JSON object.")
    return song_from_portable_payload(payload)


def song_to_portable_text(song: Song) -> str:
    """Serialize a song into the YAML-first portable authoring format."""
    yaml_text = yaml.safe_dump(
        song_to_portable_payload(song),
        sort_keys=False,
        allow_unicode=False,
    )
    return cast(str, yaml_text)


def song_from_portable_payload(payload: dict[str, Any]) -> Song:
    """Build a song from the human-authored portable payload schema."""
    raw_song = _as_dict(payload.get("song", payload), "song")
    section_models, chord_events, rhythm_cues = _parse_sections(payload)
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
        rhythm_cues=rhythm_cues,
        teacher_annotations=annotations,
    )


def song_to_portable_payload(song: Song) -> dict[str, Any]:
    """Serialize a song to the portable authoring payload."""
    chord_map = _chords_by_segment(song.chord_events)
    rhythm_map = _rhythm_by_segment(song.rhythm_cues)

    sections: list[dict[str, Any]] = []
    for section in song.lyric_sections:
        lines: list[dict[str, Any]] = []
        for segment in section.segments:
            line_payload: dict[str, Any] = {
                "id": segment.id,
                "lyrics": segment.text,
            }
            chord_events = chord_map.get(segment.id, [])
            if chord_events:
                needs_structured_chords = any(
                    _chord_needs_structured_payload(event)
                    for event in chord_events
                )
                if needs_structured_chords:
                    line_payload["chords"] = [
                        {
                            "symbol": event.chord,
                            "roman_numeral": event.roman_numeral,
                            "position": event.position,
                            "anchor": event.lyric_anchor,
                            "offset": event.lyric_offset,
                        }
                        for event in chord_events
                    ]
                else:
                    line_payload["chords"] = [
                        event.chord for event in chord_events
                    ]
                    roman_numerals = [
                        event.roman_numeral or "" for event in chord_events
                    ]
                    if any(roman_numeral for roman_numeral in roman_numerals):
                        line_payload["roman_numerals"] = roman_numerals

            if segment.melody_packages:
                line_payload["melody_packages"] = [
                    _package_to_payload(package)
                    for package in sorted(
                        segment.melody_packages,
                        key=lambda package: package.order,
                    )
                ]

            rhythm_cues = rhythm_map.get(segment.id, [])
            if rhythm_cues:
                primary_cue = rhythm_cues[0]
                if primary_cue.emphasis is None:
                    line_payload["rhythm"] = primary_cue.pattern
                else:
                    line_payload["rhythm"] = {
                        "pattern": primary_cue.pattern,
                        "emphasis": primary_cue.emphasis,
                    }

            lines.append(line_payload)

        sections.append(
            {
                "id": section.id,
                "title": section.title,
                "lines": lines,
            }
        )

    return {
        "schema_version": 2,
        "song": {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "description": song.description,
            "key_signature": song.key_signature,
            "time_signature": song.time_signature,
            "tempo_bpm": song.tempo_bpm,
            "tempo_notes": song.tempo_notes,
            "strumming_pattern": song.strumming_pattern,
        },
        "sections": sections,
        "annotations": [
            annotation.model_dump(mode="json")
            for annotation in song.teacher_annotations
        ],
    }


def _load_song_file(path: Path) -> Song:
    """Load one portable song file into a validated domain model."""
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError(f"Seed file '{path.name}' must contain an object.")

    if "lyric_sections" in payload:
        return Song.model_validate(payload)

    return song_from_portable_payload(payload)


def _parse_sections(
    payload: Mapping[str, Any],
) -> tuple[list[LyricSection], list[ChordEvent], list[RhythmCue]]:
    section_models: list[LyricSection] = []
    chord_events: list[ChordEvent] = []
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
            lyric_text = _required_str(line, "lyrics")
            segments.append(
                LyricSegment(
                    id=segment_id,
                    text=lyric_text,
                    order=line_order,
                    melody_packages=_parse_melody_packages(
                        line,
                        segment_id=segment_id,
                        lyric_text=lyric_text,
                    ),
                )
            )
            chord_events.extend(_parse_chords(line, segment_id))
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

    return section_models, chord_events, rhythm_cues


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
        lyric_anchor: str | None = None
        lyric_offset: int | None = None
        position: Literal["before", "after", "inline"] = "before"

        if isinstance(raw_chord, str):
            chord_symbol = raw_chord.strip()
            roman_numeral = _optional_list_item(roman_numerals, order)
        else:
            chord_data = _as_dict(raw_chord, f"chords[{order}]")
            chord_symbol = _required_str(chord_data, "symbol")
            roman_numeral = _optional_str(chord_data.get("roman_numeral"))
            lyric_anchor = _optional_str(chord_data.get("anchor"))
            lyric_offset = _optional_int(
                chord_data.get("offset", chord_data.get("at")),
                "offset",
            )
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
                lyric_anchor=lyric_anchor,
                lyric_offset=lyric_offset,
            )
        )

    return events


def _parse_melody_packages(
    line: Mapping[str, Any],
    *,
    segment_id: str,
    lyric_text: str,
) -> list[MelodyPackage]:
    raw_packages = line.get("melody_packages")
    raw_melody_text = line.get("melody_text")
    if raw_packages is None:
        if raw_melody_text is not None:
            raw_packages = _parse_melody_text_packages(
                raw_melody_text,
                segment_id=segment_id,
            )
        else:
            raw_legacy_melody = line.get("melody")
            if raw_legacy_melody is None:
                return []
            raw_packages = [
                {
                    "id": f"{segment_id}-pkg-1",
                    "text": lyric_text,
                    "notes": raw_legacy_melody,
                }
            ]

    packages: list[MelodyPackage] = []
    for package_order, raw_package in enumerate(
        _as_list(raw_packages, "melody_packages")
    ):
        package = _as_dict(raw_package, f"melody_packages[{package_order}]")
        package_id = _optional_str(package.get("id")) or (
            f"{segment_id}-pkg-{package_order + 1}"
        )
        notes = _parse_package_notes(
            package.get("notes"),
            segment_id=segment_id,
        )
        packages.append(
            MelodyPackage(
                id=package_id,
                text=_required_str(package, "text"),
                order=package_order,
                notes=notes,
            )
        )
    return packages


def _parse_package_notes(
    raw_notes: Any,
    *,
    segment_id: str,
) -> list[MelodyNote]:
    notes: list[MelodyNote] = []
    for note_order, raw_note in enumerate(_as_list(raw_notes, "notes")):
        if isinstance(raw_note, str):
            note, octave = _split_note_token(raw_note)
            duration_beats = 1.0
        else:
            note_data = _as_dict(raw_note, f"notes[{note_order}]")
            note, octave = _split_note_token(_required_str(note_data, "note"))
            duration_beats = float(note_data.get("beats", 1.0))

        notes.append(
            MelodyNote(
                segment_id=segment_id,
                note=note,
                octave=octave,
                duration_beats=duration_beats,
                order=note_order,
            )
        )

    if not notes:
        raise ValueError("Melody packages must contain at least one note.")
    return notes


def _parse_melody_text_packages(
    raw_melody_text: Any,
    *,
    segment_id: str,
) -> list[dict[str, Any]]:
    """Parse shorthand melody text like 'So = C,B,G' into package payloads."""
    if isinstance(raw_melody_text, str):
        melody_lines = [
            line.strip()
            for line in raw_melody_text.splitlines()
            if line.strip()
        ]
    else:
        melody_lines = [
            _required_str(
                _as_dict({"line": value}, "melody_text entry"),
                "line",
            )
            for value in _as_list(raw_melody_text, "melody_text")
        ]

    packages: list[dict[str, Any]] = []
    for package_order, line in enumerate(melody_lines):
        text_part, notes_part = _split_melody_text_line(line)
        note_tokens = _split_melody_text_notes(notes_part)
        packages.append(
            {
                "id": f"{segment_id}-pkg-{package_order + 1}",
                "text": text_part,
                "notes": note_tokens,
            }
        )
    return packages


def _split_melody_text_line(line: str) -> tuple[str, str]:
    """Split one shorthand melody line into lyric text and note sequence."""
    separator_match = re.search(r"\s*(=>|=)\s*", line)
    if separator_match is None:
        raise ValueError(
            "Each melody_text line must use 'text = notes' or "
            "'text => notes'."
        )
    text_part = line[: separator_match.start()].strip()
    notes_part = line[separator_match.end() :].strip()
    if not text_part:
        raise ValueError("Melody text packages need lyric text before '='.")
    if not notes_part:
        raise ValueError("Melody text packages need at least one note.")
    return text_part, notes_part


def _split_melody_text_notes(notes_part: str) -> list[str]:
    """Split shorthand note text into note tokens."""
    tokens = [token.strip() for token in re.split(r"[\s,]+", notes_part)]
    filtered_tokens = [token for token in tokens if token]
    if not filtered_tokens:
        raise ValueError("Melody text packages need at least one note.")
    return filtered_tokens


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


def _package_to_payload(package: MelodyPackage) -> dict[str, Any]:
    """Serialize one melody package into the portable payload shape."""
    return {
        "id": package.id,
        "text": package.text,
        "notes": [_melody_note_to_payload(note) for note in package.notes],
    }


def _melody_note_to_payload(note: MelodyNote) -> str | dict[str, Any]:
    """Serialize one melody note compactly when possible."""
    if note.duration_beats == 1.0:
        return note.display_label
    return {
        "note": note.display_label,
        "beats": note.duration_beats,
    }


def _chords_by_segment(
    chord_events: list[ChordEvent],
) -> dict[str, list[ChordEvent]]:
    """Group chord events by lyric segment."""
    grouped: dict[str, list[ChordEvent]] = {}
    for event in chord_events:
        grouped.setdefault(event.segment_id, []).append(event)
    for segment_id in grouped:
        grouped[segment_id].sort(key=lambda event: event.order)
    return grouped


def _chord_needs_structured_payload(event: ChordEvent) -> bool:
    """Return whether a chord needs the object form in portable YAML."""
    return (
        event.position != "before"
        or event.lyric_anchor is not None
        or event.lyric_offset is not None
    )


def _rhythm_by_segment(
    rhythm_cues: list[RhythmCue],
) -> dict[str, list[RhythmCue]]:
    """Group rhythm cues by lyric segment."""
    grouped: dict[str, list[RhythmCue]] = {}
    for cue in rhythm_cues:
        grouped.setdefault(cue.segment_id, []).append(cue)
    return grouped


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
        raise ValueError(f"{label} must be a mapping object.")
    return value


def _as_list(value: Any, label: str) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    raise ValueError(f"{label} must be a list.")


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
