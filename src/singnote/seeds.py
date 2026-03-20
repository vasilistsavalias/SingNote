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
    return [_build_wish_you_were_here()]


def _build_wish_you_were_here() -> Song:
    """Build the seeded Pink Floyd lesson song."""
    return Song(
        id="wish-you-were-here",
        title="Wish You Were Here",
        artist="Pink Floyd",
        description=(
            "Sourced harmony and rhythm guide in G major with manual melody "
            "dictation for lesson use."
        ),
        key_signature="G major",
        time_signature="4/4",
        tempo_bpm=61,
        tempo_notes=(
            "Many practice references feel the song around 61 BPM, while some "
            "tempo analyzers list it near 122 BPM in double-time."
        ),
        strumming_pattern=(
            "Feel the song in even 8ths. Common lesson pattern per bar pair: "
            "D D U | D D U U, with the intro kept lighter and more ringing."
        ),
        lyric_sections=_wish_lyric_sections(),
        chord_events=_wish_chord_events(),
        melody_notes=_wish_melody_notes(),
        rhythm_cues=_wish_rhythm_cues(),
        teacher_annotations=_wish_annotations("wish-you-were-here"),
    )


def _wish_lyric_sections() -> list[LyricSection]:
    """Return short lyric snippets for the seeded lesson card."""
    return [
        _build_section(
            "intro",
            "Intro",
            [
                "Instrumental intro figure 1",
                "Instrumental intro figure 2",
            ],
            0,
        ),
        _build_section(
            "verse-1",
            "Verse 1",
            [
                "So so you think",
                "Heaven from hell",
                "Blue skies from pain",
                "Can you tell",
                "Cold steel rail",
                "Smile from a veil",
                "Do you think",
            ],
            1,
        ),
        _build_section(
            "verse-2",
            "Verse 2",
            [
                "Did they get you",
                "Heroes from ghosts",
                "Hot ashes for trees",
                "Cool breeze",
                "Cold comfort",
                "Did you exchange",
                "Walk on part",
                "Lead role in a cage",
            ],
            2,
        ),
        _build_section(
            "chorus",
            "Chorus",
            [
                "How I wish",
                "Two souls swimming",
                "Year after year",
                "Same old ground",
                "What have we found",
                "Same old fears",
                "Wish you were here",
            ],
            3,
        ),
    ]


def _build_section(
    section_id: str,
    title: str,
    lines: list[str],
    order: int,
) -> LyricSection:
    """Build a phrase-oriented lyric section."""
    return LyricSection(
        id=section_id,
        title=title,
        order=order,
        segments=[
            LyricSegment(
                id=f"{section_id}-{index + 1}",
                text=line,
                order=index,
            )
            for index, line in enumerate(lines)
        ],
    )


def _wish_chord_events() -> list[ChordEvent]:
    """Return sourced harmony labels for the lesson card."""
    return [
        *_chord_series(
            "intro-1",
            [("Em7", "vi7"), ("G", "I"), ("Em7", "vi7"), ("G", "I")],
        ),
        *_chord_series(
            "intro-2",
            [
                ("Em7", "vi7"),
                ("A7sus4", "II7sus4"),
                ("Em7", "vi7"),
                ("A7sus4", "II7sus4"),
                ("G", "I"),
            ],
        ),
        *_chord_series("verse-1-1", [("C", "IV"), ("D/F#", "V/3")]),
        *_chord_series("verse-1-2", [("Am", "ii")]),
        *_chord_series("verse-1-3", [("G", "I")]),
        *_chord_series("verse-1-4", [("D/F#", "V/3")]),
        *_chord_series("verse-1-5", [("C", "IV")]),
        *_chord_series("verse-1-6", [("Am", "ii")]),
        *_chord_series("verse-1-7", [("G", "I")]),
        *_chord_series("verse-2-1", [("C", "IV")]),
        *_chord_series("verse-2-2", [("D/F#", "V/3")]),
        *_chord_series("verse-2-3", [("Am", "ii")]),
        *_chord_series("verse-2-4", [("G", "I")]),
        *_chord_series("verse-2-5", [("D/F#", "V/3")]),
        *_chord_series("verse-2-6", [("C", "IV")]),
        *_chord_series("verse-2-7", [("Am", "ii")]),
        *_chord_series("verse-2-8", [("G", "I")]),
        *_chord_series("chorus-1", [("C", "IV"), ("D/F#", "V/3")]),
        *_chord_series("chorus-2", [("Am", "ii"), ("G", "I")]),
        *_chord_series("chorus-3", [("D/F#", "V/3")]),
        *_chord_series("chorus-4", [("D/F#", "V/3")]),
        *_chord_series("chorus-5", [("C", "IV")]),
        *_chord_series("chorus-6", [("Am", "ii")]),
        *_chord_series("chorus-7", [("G", "I")]),
    ]


def _chord_series(
    segment_id: str,
    chords: list[tuple[str, str | None]],
) -> list[ChordEvent]:
    """Build ordered chord events for a single phrase."""
    return [
        ChordEvent(
            segment_id=segment_id,
            chord=chord,
            roman_numeral=roman_numeral,
            order=index,
        )
        for index, (chord, roman_numeral) in enumerate(chords)
    ]


def _wish_melody_notes() -> list[MelodyNote]:
    """Return the manually supplied melody dictation."""
    return [
        *_melody_series(
            "verse-1-1",
            ["C", "B", "G", "C", "B", "C", "B", "G", "A"],
        ),
        *_melody_series("verse-1-2", ["D", "B", "D", "E"]),
        *_melody_series("verse-1-3", ["E", "E", "C", "D"]),
        *_melody_series("verse-1-4", ["C", "B", "C", "B", "G", "A"]),
        *_melody_series("verse-1-5", ["D", "D", "D", "C", "B", "C", "B", "A"]),
        *_melody_series("verse-1-6", ["C", "D", "C", "B", "C"]),
        *_melody_series("verse-1-7", ["C", "B", "C", "B", "G", "A"]),
        *_melody_series("verse-2-1", ["D", "D", "D", "C", "D", "E"]),
        *_melody_series("verse-2-2", ["E", "E", "D", "C", "D"]),
        *_melody_series("verse-2-3", ["D", "D", "D", "C", "D", "E"]),
        *_melody_series("verse-2-4", ["E", "E", "D", "C", "D", "D"]),
        *_melody_series("verse-2-5", ["D", "C", "B", "G", "A"]),
        *_melody_series("verse-2-6", ["D", "D", "C", "B", "C", "B", "A"]),
        *_melody_series("verse-2-7", ["B", "C", "B", "C", "B", "G", "A"]),
        *_melody_series("verse-2-8", ["B", "B", "C", "B", "A", "G", "A"]),
        *_melody_series(
            "chorus-1",
            ["B", "C", "B", "B", "C", "B", "G", "G", "A"],
        ),
        *_melody_series(
            "chorus-2",
            ["B", "D", "E", "E", "E", "E", "D", "E", "D", "E", "E"],
        ),
        *_melody_series("chorus-3", ["D", "D", "B", "D"]),
        *_melody_series("chorus-4", ["D", "D", "D", "B", "D", "B"]),
        *_melody_series("chorus-5", ["C", "D", "C", "D", "C", "B", "G"]),
        *_melody_series("chorus-6", ["D", "C", "B", "C", "B", "G"]),
        *_melody_series("chorus-7", ["C", "C", "G", "C", "B", "G"]),
    ]


def _melody_series(
    segment_id: str,
    notes: list[str],
) -> list[MelodyNote]:
    """Build ordered melody notes for a phrase."""
    return [
        MelodyNote(
            segment_id=segment_id,
            note=note,
            duration_beats=1.0,
            order=index,
        )
        for index, note in enumerate(notes)
    ]


def _wish_rhythm_cues() -> list[RhythmCue]:
    """Return rhythm and groove guidance for each phrase."""
    return [
        RhythmCue(
            segment_id="intro-1",
            pattern="steady 8ths",
            emphasis="let open strings ring",
        ),
        RhythmCue(
            segment_id="intro-2",
            pattern="steady 8ths",
            emphasis="lean into the sus push before G",
        ),
        RhythmCue(
            segment_id="verse-1-1",
            pattern="2-bar pickup",
            emphasis="change chord mid-line",
        ),
        RhythmCue(
            segment_id="verse-1-2",
            pattern="held line ending",
            emphasis="do not rush beat 4",
        ),
        RhythmCue(segment_id="verse-1-3", pattern="even 8ths"),
        RhythmCue(segment_id="verse-1-4", pattern="even 8ths"),
        RhythmCue(segment_id="verse-1-5", pattern="even 8ths"),
        RhythmCue(segment_id="verse-1-6", pattern="held cadence"),
        RhythmCue(segment_id="verse-1-7", pattern="question tag"),
        RhythmCue(segment_id="verse-2-1", pattern="even 8ths"),
        RhythmCue(segment_id="verse-2-2", pattern="even 8ths"),
        RhythmCue(segment_id="verse-2-3", pattern="even 8ths"),
        RhythmCue(segment_id="verse-2-4", pattern="even 8ths"),
        RhythmCue(segment_id="verse-2-5", pattern="slightly lighter"),
        RhythmCue(segment_id="verse-2-6", pattern="cadential pickup"),
        RhythmCue(segment_id="verse-2-7", pattern="build into chorus"),
        RhythmCue(segment_id="verse-2-8", pattern="land the final bar"),
        RhythmCue(segment_id="chorus-1", pattern="open the sound"),
        RhythmCue(segment_id="chorus-2", pattern="keep the pulse floating"),
        RhythmCue(segment_id="chorus-3", pattern="short answer line"),
        RhythmCue(segment_id="chorus-4", pattern="steady forward motion"),
        RhythmCue(segment_id="chorus-5", pattern="cadential answer"),
        RhythmCue(segment_id="chorus-6", pattern="soften the landing"),
        RhythmCue(segment_id="chorus-7", pattern="final tag"),
    ]


def _wish_annotations(song_id: str) -> list[TeacherAnnotation]:
    """Return coaching notes for the seeded lesson card."""
    return [
        TeacherAnnotation(
            target_type="song",
            target_id=song_id,
            text=(
                "Key center is G major, but the intro opens on Em7 so the "
                "relative-minor color should still feel present."
            ),
        ),
        TeacherAnnotation(
            target_type="song",
            target_id=song_id,
            text=(
                "Use the shared authoring panel to replace these short seed "
                "your licensed full lyric text when teaching."
            ),
        ),
        TeacherAnnotation(
            target_type="song",
            target_id=song_id,
            text=(
                "Melody notes were entered from the provided dictation and can "
                "be corrected in place with the tap note editor."
            ),
        ),
        TeacherAnnotation(
            target_type="section",
            target_id="chorus",
            text="Open the tone in the chorus and keep the groove relaxed.",
        ),
    ]
