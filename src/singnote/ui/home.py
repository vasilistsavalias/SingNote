"""Home page UI for the bootstrapped application."""

from __future__ import annotations

import re
from typing import Any

import streamlit as st

from singnote.auth import resolve_app_access, validate_shared_login
from singnote.bootstrap import Application
from singnote.components.long_press_note_editor import long_press_note_editor
from singnote.domain.models import MelodyNote, Song
from singnote.ui.authoring import (
    SongEditorValues,
    blank_editor_values,
    build_song_from_editor_values,
    editor_values_from_song,
)


def render_home_page(app: Application) -> None:
    """Render the initial landing page for the application."""
    st.set_page_config(
        page_title=app.settings.app_name,
        page_icon=":musical_note:",
        layout="wide",
    )
    if not _render_access_gate(app):
        return

    _render_sidebar_status()
    st.title("SingNote")
    st.caption("Structured singing practice for student and teacher.")

    songs = app.repository.list_songs()
    _render_authoring_panel(app, songs)

    st.subheader("Song Catalog")
    if not songs:
        st.info(
            "No songs are available yet. The authoring workflow will populate "
            "this catalog soon."
        )
        return

    for song in songs:
        with st.container(border=True):
            st.markdown(f"### {song.title}")
            if song.artist:
                st.write(song.artist)
            if song.description:
                st.caption(song.description)
            stats = [
                f"{len(song.lyric_sections)} sections",
                f"{len(song.melody_notes)} melody notes",
                f"{len(song.rhythm_cues)} rhythm cues",
            ]
            st.write(" | ".join(stats))


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
                    help="One per line: segment-id|Chord|position",
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
                    height=120,
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
                if editor_target != "__new__":
                    song.melody_notes = song_lookup[editor_target].melody_notes
                app.repository.upsert_song(song)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(f"Saved {song.title}.")
                st.rerun()

        if editor_target == "__new__":
            return

        current_song = song_lookup[editor_target]
        st.markdown("#### Melody quick editor")
        update = long_press_note_editor(
            notes=_melody_note_payload(current_song),
            key=f"melody-editor-{current_song.id}",
        )
        if update is None:
            return
        try:
            _apply_melody_update(current_song, update)
            app.repository.upsert_song(current_song)
        except ValueError as error:
            st.error(str(error))
            return
        st.success("Updated melody note.")
        st.rerun()


def _melody_note_payload(song: Song) -> list[dict[str, object]]:
    """Serialize melody notes into component-friendly payloads."""
    lyric_lookup = {}
    for section in song.lyric_sections:
        for segment in section.segments:
            lyric_lookup[segment.id] = segment.text

    return [
        {
            "segment_id": note.segment_id,
            "note_label": f"{note.note}{note.octave}",
            "duration_beats": note.duration_beats,
            "lyric": lyric_lookup.get(note.segment_id, note.segment_id),
        }
        for note in song.melody_notes
    ]


def _apply_melody_update(song: Song, update: dict[str, Any]) -> None:
    """Apply a component note update to a song and validate it."""
    segment_id = str(update["segment_id"])
    note_token = str(update["note_label"]).strip()
    duration_beats = float(update["duration_beats"])
    replacement = _parse_note_token(segment_id, note_token, duration_beats)

    new_notes = []
    replaced = False
    for note in song.melody_notes:
        if note.segment_id == segment_id:
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
) -> MelodyNote:
    """Convert a note token like C4 into a melody note object."""
    match = re.fullmatch(r"([A-Ga-g][#b]?)(\d)", note_token)
    if match is None:
        raise ValueError("Use note names like C4 or F#4.")
    return MelodyNote(
        segment_id=segment_id,
        note=match.group(1).upper(),
        octave=int(match.group(2)),
        duration_beats=duration_beats,
    )
