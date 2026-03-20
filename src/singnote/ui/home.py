"""Home page UI for the bootstrapped application."""

from __future__ import annotations

import re
from typing import Any

import streamlit as st

from singnote.auth import resolve_app_access, validate_shared_login
from singnote.bootstrap import Application
from singnote.components.long_press_note_editor import long_press_note_editor
from singnote.domain.models import (
    ChordEvent,
    MelodyNote,
    RhythmCue,
    Song,
)
from singnote.ui.authoring import (
    SongEditorValues,
    blank_editor_values,
    build_song_from_editor_values,
    editor_values_from_song,
)
from singnote.ui.theme import inject_global_styles, render_hero


def render_home_page(app: Application) -> None:
    """Render the initial landing page for the application."""
    st.set_page_config(
        page_title=app.settings.app_name,
        page_icon=":musical_note:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_global_styles()
    if not _render_access_gate(app):
        return

    _render_sidebar_status()

    songs = app.repository.list_songs()
    render_hero(len(songs))
    _render_authoring_panel(app, songs)

    st.subheader("Song Catalog")
    if not songs:
        st.info(
            "No songs are available yet. The authoring workflow will populate "
            "this catalog soon."
        )
        return

    song_lookup = {song.id: song for song in songs}
    _render_catalog(song_lookup)
    _render_workspace(app, song_lookup)


def _render_access_gate(app: Application) -> bool:
    """Render a shared username/password login screen when configured."""
    access = resolve_app_access(
        app.settings.shared_username,
        app.settings.shared_password,
        bool(st.session_state.get("app_authenticated", False)),
    )
    if access.app_access_enabled:
        return True

    left, center, right = st.columns([1, 1.1, 1])
    with center:
        st.title("SingNote Login")
        st.caption("Use the shared teacher/student account to enter the app.")
        with st.form("shared-login-form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Enter SingNote")
        if submitted:
            if validate_shared_login(
                username,
                password,
                app.settings.shared_username,
                app.settings.shared_password,
            ):
                st.session_state["app_authenticated"] = True
                st.rerun()
            st.error("Incorrect username or password.")
    return False


def _render_sidebar_status() -> None:
    """Render shared-session status in the sidebar."""
    st.sidebar.header("Session")
    if st.sidebar.button("Log out"):
        st.session_state["app_authenticated"] = False
        st.rerun()
    st.sidebar.success("Logged in with the shared teaching account.")


def _render_authoring_panel(app: Application, songs: list[Song]) -> None:
    """Render the MVP create and edit workflow."""
    with st.expander("Create or edit songs", expanded=False):
        song_lookup = {song.id: song for song in songs}
        editor_target = st.selectbox(
            "Song to edit",
            options=["__new__"] + list(song_lookup.keys()),
            format_func=lambda value: (
                "Create new song"
                if value == "__new__"
                else song_lookup[value].title
            ),
        )
        defaults = (
            blank_editor_values()
            if editor_target == "__new__"
            else editor_values_from_song(song_lookup[editor_target])
        )
        with st.form("song-authoring-form"):
            values = SongEditorValues(
                song_id=st.text_input(
                    "Song id",
                    value=defaults.song_id,
                    help="Leave blank to derive an id from the title.",
                ),
                title=st.text_input("Title", value=defaults.title),
                artist=st.text_input("Artist", value=defaults.artist),
                description=st.text_area(
                    "Description",
                    value=defaults.description,
                    height=80,
                ),
                key_signature=st.text_input(
                    "Key signature",
                    value=defaults.key_signature,
                ),
                time_signature=st.text_input(
                    "Time signature",
                    value=defaults.time_signature,
                ),
                tempo_bpm=st.text_input(
                    "Tempo (BPM)",
                    value=defaults.tempo_bpm,
                ),
                tempo_notes=st.text_area(
                    "Tempo notes",
                    value=defaults.tempo_notes,
                    height=80,
                ),
                strumming_pattern=st.text_area(
                    "Strumming pattern",
                    value=defaults.strumming_pattern,
                    height=80,
                ),
                lyrics_text=st.text_area(
                    "Lyrics structure",
                    value=defaults.lyrics_text,
                    height=180,
                    help=(
                        "Use [Section Name] headers and lyric words below "
                        "them."
                    ),
                ),
                chords_text=st.text_area(
                    "Chords",
                    value=defaults.chords_text,
                    height=120,
                    help=(
                        "One per line: segment-id|Chord|RomanNumeral|position"
                    ),
                ),
                melody_text=st.text_area(
                    "Melody seed text",
                    value=defaults.melody_text,
                    height=120,
                    disabled=editor_target != "__new__",
                    help=(
                        "For existing songs, edit melody notes below by long "
                        "pressing the note chip."
                    ),
                ),
                rhythm_text=st.text_area(
                    "Rhythm",
                    value=defaults.rhythm_text,
                    height=120,
                    help="One per line: segment-id|pattern|optional-emphasis",
                ),
                annotations_text=st.text_area(
                    "Teacher annotations",
                    value=defaults.annotations_text,
                    height=140,
                    help=(
                        "One per line: song|song-id|text or "
                        "segment|segment-id|text"
                    ),
                ),
            )
            submitted = st.form_submit_button("Save song")

        if submitted:
            try:
                song = build_song_from_editor_values(values)
                app.repository.upsert_song(song)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(f"Saved {song.title}.")
                st.rerun()


def _render_catalog(song_lookup: dict[str, Song]) -> None:
    """Render responsive song cards and workspace entry buttons."""
    songs = list(song_lookup.values())
    columns = st.columns(2)
    for index, song in enumerate(songs):
        with columns[index % 2], st.container(border=True):
            st.markdown(f"### {song.title}")
            if song.artist:
                st.write(song.artist)
            if song.description:
                st.caption(song.description)
            summary = _song_summary(song)
            if summary:
                st.caption(summary)
            if st.button(
                "Open workspace",
                key=f"open-song-{song.id}",
                use_container_width=True,
            ):
                st.session_state["selected_song_id"] = song.id
                st.rerun()


def _render_workspace(app: Application, song_lookup: dict[str, Song]) -> None:
    """Render the selected song workspace with learning tabs."""
    selected_song_id = st.session_state.get("selected_song_id")
    if selected_song_id not in song_lookup:
        selected_song_id = next(iter(song_lookup))
        st.session_state["selected_song_id"] = selected_song_id
    song = song_lookup[selected_song_id]

    st.divider()
    st.subheader(song.title)
    if song.artist:
        st.caption(song.artist)
    if song.key_signature or song.time_signature or song.tempo_bpm:
        st.caption(_song_summary(song))

    lyrics_tab, melody_tab, rhythm_tab = st.tabs(
        ["Lyrics + Chords", "Melody", "Rhythm"]
    )

    with lyrics_tab:
        _render_lyrics_tab(song)
    with melody_tab:
        _render_melody_tab(app, song)
    with rhythm_tab:
        _render_rhythm_tab(song)


def _render_lyrics_tab(song: Song) -> None:
    """Render lyric phrases with their chord guidance."""
    chord_map = _chords_by_segment(song.chord_events)
    for section in song.lyric_sections:
        st.markdown(f"### {section.title or section.id}")
        for segment in section.segments:
            with st.container(border=True):
                chords = chord_map.get(segment.id, [])
                if chords:
                    st.caption(
                        "  |  ".join(
                            _format_chord(event) for event in chords
                        )
                    )
                st.write(segment.text)


def _render_melody_tab(app: Application, song: Song) -> None:
    """Render melody dictation and in-place note editing."""
    melody_map = _melody_by_segment(song.melody_notes)
    for section in song.lyric_sections:
        st.markdown(f"### {section.title or section.id}")
        for segment in section.segments:
            with st.container(border=True):
                notes = melody_map.get(segment.id, [])
                if notes:
                    st.caption("  ".join(note.display_label for note in notes))
                else:
                    st.caption("No melody notes entered yet.")
                st.write(segment.text)

        update = long_press_note_editor(
            notes=_melody_note_payload(song, section.id),
            key=f"melody-editor-{song.id}-{section.id}",
        )
        if update is None:
            continue
        try:
            _apply_melody_update(song, update)
            app.repository.upsert_song(song)
        except ValueError as error:
            st.error(str(error))
            return
        st.success("Updated melody note.")
        st.rerun()


def _render_rhythm_tab(song: Song) -> None:
    """Render rhythm and theory guidance for the song."""
    stat_columns = st.columns(3)
    with stat_columns[0]:
        st.metric("Key", song.key_signature or "Unknown")
    with stat_columns[1]:
        st.metric("Time", song.time_signature or "Unknown")
    with stat_columns[2]:
        tempo_label = f"{song.tempo_bpm} BPM" if song.tempo_bpm else "Unknown"
        st.metric("Tempo", tempo_label)

    if song.strumming_pattern:
        st.markdown("### Strumming Pattern")
        st.code(song.strumming_pattern)
    if song.tempo_notes:
        st.info(song.tempo_notes)

    st.markdown("### Rhythm Cues")
    rhythm_map = _rhythm_by_segment(song.rhythm_cues)
    for section in song.lyric_sections:
        st.markdown(f"#### {section.title or section.id}")
        for segment in section.segments:
            cues = rhythm_map.get(segment.id, [])
            if not cues:
                continue
            for cue in cues:
                emphasis = f" ({cue.emphasis})" if cue.emphasis else ""
                st.write(f"{segment.text}: {cue.pattern}{emphasis}")

    song_notes = [
        annotation
        for annotation in song.teacher_annotations
        if annotation.target_type == "song"
    ]
    if song_notes:
        st.markdown("### Guidance Notes")
        for note in song_notes:
            st.write(f"- {note.text}")


def _song_summary(song: Song) -> str:
    """Return a short metadata summary for catalog cards and workspace."""
    parts = []
    if song.key_signature:
        parts.append(song.key_signature)
    if song.time_signature:
        parts.append(song.time_signature)
    if song.tempo_bpm:
        parts.append(f"{song.tempo_bpm} BPM")
    return " · ".join(parts)


def _format_chord(event: ChordEvent) -> str:
    """Format a chord label with optional roman numeral guidance."""
    return (
        f"{event.chord} [{event.roman_numeral}]"
        if event.roman_numeral
        else event.chord
    )


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


def _melody_by_segment(
    melody_notes: list[MelodyNote],
) -> dict[str, list[MelodyNote]]:
    """Group melody notes by lyric segment."""
    grouped: dict[str, list[MelodyNote]] = {}
    for note in melody_notes:
        grouped.setdefault(note.segment_id, []).append(note)
    for segment_id in grouped:
        grouped[segment_id].sort(key=lambda note: note.order)
    return grouped


def _rhythm_by_segment(
    rhythm_cues: list[RhythmCue],
) -> dict[str, list[RhythmCue]]:
    """Group rhythm cues by lyric segment."""
    grouped: dict[str, list[RhythmCue]] = {}
    for cue in rhythm_cues:
        grouped.setdefault(cue.segment_id, []).append(cue)
    return grouped


def _melody_note_payload(
    song: Song,
    section_id: str | None = None,
) -> list[dict[str, object]]:
    """Serialize melody notes into component-friendly payloads."""
    lyric_lookup = {}
    segment_to_section = {}
    for section in song.lyric_sections:
        for segment in section.segments:
            lyric_lookup[segment.id] = segment.text
            segment_to_section[segment.id] = section.id

    payload = []
    for note in song.melody_notes:
        if section_id and segment_to_section.get(note.segment_id) != section_id:
            continue
        payload.append(
            {
                "segment_id": note.segment_id,
                "order": note.order,
                "note_label": note.display_label,
                "duration_beats": note.duration_beats,
                "lyric": lyric_lookup.get(note.segment_id, note.segment_id),
            }
        )
    return payload


def _apply_melody_update(song: Song, update: dict[str, Any]) -> None:
    """Apply a component note update to a song and validate it."""
    segment_id = str(update["segment_id"])
    note_order = int(update["order"])
    note_token = str(update["note_label"]).strip()
    duration_beats = float(update["duration_beats"])
    replacement = _parse_note_token(
        segment_id,
        note_token,
        duration_beats,
        note_order,
    )

    new_notes = []
    replaced = False
    for note in song.melody_notes:
        if note.segment_id == segment_id and note.order == note_order:
            new_notes.append(replacement)
            replaced = True
        else:
            new_notes.append(note)

    if not replaced:
        raise ValueError(
            "Selected note could not be matched to a song segment."
        )

    song.melody_notes = new_notes
    Song.model_validate(song.model_dump())


def _parse_note_token(
    segment_id: str,
    note_token: str,
    duration_beats: float,
    order: int = 0,
) -> MelodyNote:
    """Convert a note token like C or C4 into a melody note object."""
    match = re.fullmatch(r"([A-Ga-g][#b]?)(\d)?", note_token)
    if match is None:
        raise ValueError("Use note names like C, C4, or F#4.")
    octave = int(match.group(2)) if match.group(2) else None
    return MelodyNote(
        segment_id=segment_id,
        note=match.group(1).upper(),
        octave=octave,
        duration_beats=duration_beats,
        order=order,
    )
