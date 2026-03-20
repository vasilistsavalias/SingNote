"""Home page UI for the bootstrapped application."""

from __future__ import annotations

import re
from html import escape
from typing import TypeVar

import streamlit as st
import streamlit.components.v1 as components

from singnote.auth import resolve_app_access, validate_shared_login
from singnote.bootstrap import Application
from singnote.domain.models import (
    ChordEvent,
    LyricSection,
    LyricSegment,
    MelodyNote,
    MelodyPackage,
    RhythmCue,
    Song,
)
from singnote.ui.authoring import (
    SongEditorValues,
    blank_editor_values,
    build_song_from_editor_values,
    build_song_from_yaml_text,
    editor_values_from_song,
    yaml_text_from_song,
)
from singnote.ui.theme import inject_global_styles

T = TypeVar("T")


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

    songs = app.repository.list_songs()
    _render_sidebar_status(app, songs)
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


def _render_sidebar_status(app: Application, songs: list[Song]) -> None:
    """Render shared-session status in the sidebar."""
    st.sidebar.header("Session")
    if st.sidebar.button("Log out"):
        st.session_state["app_authenticated"] = False
        st.rerun()
    st.sidebar.success("Logged in with the shared teaching account.")
    _render_sidebar_settings(app, songs)


def _render_sidebar_settings(app: Application, songs: list[Song]) -> None:
    """Render song-level tools under a compact sidebar settings control."""
    song_lookup = {song.id: song for song in songs}
    seed_song_ids = [
        song_id for song_id in song_lookup if song_id in app.seed_songs
    ]
    selected_song_id = st.session_state.get("selected_song_id")
    if selected_song_id not in song_lookup and songs:
        selected_song_id = songs[0].id

    with st.sidebar.popover(
        "Settings",
        icon=":material/settings:",
        use_container_width=True,
    ):
        st.caption("Song tools")
        if not seed_song_ids:
            st.write("No resettable seed songs are available.")
            return

        default_index = (
            seed_song_ids.index(selected_song_id)
            if selected_song_id in seed_song_ids
            else 0
        )
        reset_song_id = st.selectbox(
            "Seed song",
            options=seed_song_ids,
            index=default_index,
            format_func=lambda value: song_lookup[value].title,
            key="sidebar-seed-song",
        )
        st.caption(
            "Reset replaces the current database version with the YAML seed."
        )
        confirm_reset = st.checkbox(
            "I understand this will discard in-app edits for this song.",
            key="sidebar-reset-confirm",
        )
        if st.button(
            "Reset from seed",
            key="sidebar-reset-seed",
            use_container_width=True,
            disabled=not confirm_reset,
        ):
            app.repository.reset_song_to_seed(app.seed_songs[reset_song_id])
            st.session_state["selected_song_id"] = reset_song_id
            st.success(
                f"Reset {song_lookup[reset_song_id].title} from seed YAML."
            )
            st.rerun()


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
        yaml_defaults = (
            _blank_song_yaml_text()
            if editor_target == "__new__"
            else yaml_text_from_song(song_lookup[editor_target])
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
                        "Use [Section Name] headers and one lyric line per "
                        "line below them."
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
                    "Legacy melody seed text",
                    value=defaults.melody_text,
                    height=120,
                    disabled=editor_target != "__new__",
                    help=(
                        "Use the YAML editor or melody package controls for "
                        "real melody authoring."
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

        st.markdown("#### Portable Song YAML")
        st.caption(
            "Edit package-based melody data here for seed files or advanced "
            "manual authoring."
        )
        yaml_text = st.text_area(
            "Song YAML",
            value=yaml_defaults,
            height=340,
            key=f"song-yaml-{editor_target}",
        )
        if st.button(
            "Save YAML song",
            key=f"save-yaml-song-{editor_target}",
            use_container_width=True,
        ):
            try:
                song = build_song_from_yaml_text(yaml_text)
                app.repository.upsert_song(song)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(f"Saved {song.title} from YAML.")
                st.session_state["selected_song_id"] = song.id
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
    """Render the lyrics tab as a continuous chord chart."""
    _render_auto_scroll_controls("lyrics")
    st.markdown(_lyrics_sheet_markup(song), unsafe_allow_html=True)


def _render_melody_tab(app: Application, song: Song) -> None:
    """Render melody dictation as package-based grouped line cards."""
    _render_auto_scroll_controls("melody")
    for section in song.lyric_sections:
        section_segments = [
            segment
            for segment in section.segments
            if _should_render_melody_segment(segment)
        ]
        if not section_segments:
            continue
        st.markdown(f"### {section.title or section.id}")
        for segment in section_segments:
            _render_melody_segment_card(
                app,
                song,
                section,
                segment,
            )


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


def _render_melody_segment_card(
    app: Application,
    song: Song,
    section: LyricSection,
    segment: LyricSegment,
) -> None:
    """Render one line of melody packages with per-package editing."""
    with st.container(border=True):
        st.caption(segment.text)
        packages = sorted(
            segment.melody_packages,
            key=lambda package: package.order,
        )

        for package_chunk in _chunked(packages, 4):
            columns = st.columns(len(package_chunk))
            for column, package in zip(columns, package_chunk, strict=True):
                with column:
                    st.markdown(
                        _melody_package_markup(package),
                        unsafe_allow_html=True,
                    )
                    with st.popover(
                        "Edit",
                        icon=":material/edit:",
                        use_container_width=True,
                    ):
                        st.caption(section.title or section.id)
                        package_text = st.text_input(
                            "Package text",
                            value=package.text,
                            key=(
                                f"package-text-{song.id}-{segment.id}-"
                                f"{package.id}"
                            ),
                        )
                        notes_value = st.text_area(
                            "Package notes",
                            value=_format_package_note_sequence(package),
                            height=120,
                            help=(
                                "Use notes like C, Bb, or F#4 separated by "
                                "commas or spaces."
                            ),
                            key=(
                                f"package-notes-{song.id}-{segment.id}-"
                                f"{package.id}"
                            ),
                        )
                        if st.button(
                            "Save package",
                            key=(
                                f"package-save-{song.id}-{segment.id}-"
                                f"{package.id}"
                            ),
                            use_container_width=True,
                        ):
                            try:
                                _update_melody_package(
                                    song,
                                    segment_id=segment.id,
                                    package_id=package.id,
                                    package_text=package_text,
                                    notes_text=notes_value,
                                )
                                app.repository.upsert_song(song)
                            except ValueError as error:
                                st.error(str(error))
                            else:
                                st.success("Updated melody package.")
                                st.rerun()

                        add_before_clicked = st.button(
                            "Add before",
                            key=(
                                f"package-add-before-{song.id}-{segment.id}-"
                                f"{package.id}"
                            ),
                            use_container_width=True,
                        )
                        add_after_clicked = st.button(
                            "Add after",
                            key=(
                                f"package-add-after-{song.id}-{segment.id}-"
                                f"{package.id}"
                            ),
                            use_container_width=True,
                        )
                        delete_clicked = st.button(
                            "Delete package",
                            key=(
                                f"package-delete-{song.id}-{segment.id}-"
                                f"{package.id}"
                            ),
                            use_container_width=True,
                        )

                        if add_before_clicked:
                            _insert_melody_package(
                                song,
                                segment_id=segment.id,
                                anchor_package_id=package.id,
                                position="before",
                            )
                            app.repository.upsert_song(song)
                            st.rerun()
                        if add_after_clicked:
                            _insert_melody_package(
                                song,
                                segment_id=segment.id,
                                anchor_package_id=package.id,
                                position="after",
                            )
                            app.repository.upsert_song(song)
                            st.rerun()
                        if delete_clicked:
                            _delete_melody_package(
                                song,
                                segment_id=segment.id,
                                package_id=package.id,
                            )
                            app.repository.upsert_song(song)
                            st.rerun()


def _song_summary(song: Song) -> str:
    """Return a short metadata summary for catalog cards and workspace."""
    parts = []
    if song.key_signature:
        parts.append(song.key_signature)
    if song.time_signature:
        parts.append(song.time_signature)
    if song.tempo_bpm:
        parts.append(f"{song.tempo_bpm} BPM")
    return " | ".join(parts)


def _blank_song_yaml_text() -> str:
    """Return a starter portable YAML scaffold for a new song."""
    return "\n".join(
        [
            "song:",
            "  id: new-song",
            "  title: New Song",
            "  artist: ''",
            "  description: ''",
            "  key_signature: C major",
            "  time_signature: 4/4",
            "  tempo_bpm: 60",
            "sections:",
            "  - id: verse-1",
            "    title: Verse 1",
            "    lines:",
            "      - lyrics: Type the lyric line here",
            "        chords: [C]",
            "        melody_packages:",
            "          - text: Type",
            "            notes: [C]",
            "annotations: []",
        ]
    )


def _lyrics_sheet_markup(song: Song) -> str:
    """Render the lyrics tab as one continuous chart sheet."""
    chord_map = _chords_by_segment(song.chord_events)
    sections_markup: list[str] = []
    for section in song.lyric_sections:
        visible_segments = [
            segment
            for segment in section.segments
            if not _is_instrumental_segment(segment)
        ]
        if not visible_segments:
            continue
        section_lines = [
            _lyrics_sheet_line_markup(
                segment.text,
                chord_map.get(segment.id, []),
            )
            for segment in visible_segments
        ]
        sections_markup.append(
            "".join(
                [
                    '<section class="sn-sheet-section">',
                    (
                        f'<div class="sn-sheet-section-title">'
                        f"{escape(section.title or section.id)}"
                        "</div>"
                    ),
                    "".join(section_lines),
                    "</section>",
                ]
            )
        )

    return "".join(
        [
            '<div class="sn-song-sheet">',
            "".join(sections_markup),
            "</div>",
        ]
    )


def _lyrics_sheet_line_markup(
    lyric: str,
    chords: list[ChordEvent],
) -> str:
    """Render one chart line with chords above the lyric text."""
    chord_line = ""
    if chords:
        chord_line = "".join(
            [
                '<div class="sn-sheet-chords">',
                "".join(
                    f'<span class="sn-sheet-chord">'
                    f"{escape(_format_chord(chord))}</span>"
                    for chord in chords
                ),
                "</div>",
            ]
        )
    return "".join(
        [
            '<div class="sn-sheet-line">',
            chord_line,
            f'<div class="sn-sheet-lyric">{escape(lyric)}</div>',
            "</div>",
        ]
    )


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


def _melody_package_markup(package: MelodyPackage) -> str:
    """Render one melody package block with grouped notes and lyric text."""
    return "".join(
        [
            '<div class="sn-melody-package">',
            (
                f'<div class="sn-melody-package-notes">'
                f"{escape(_format_package_note_sequence(package))}</div>"
            ),
            (
                f'<div class="sn-melody-package-text">'
                f"{escape(package.text)}</div>"
            ),
            "</div>",
        ]
    )


def _format_package_note_sequence(package: MelodyPackage) -> str:
    """Render package notes as a readable grouped string."""
    return " ".join(note.display_label for note in package.notes)


def _render_auto_scroll_controls(scope_key: str) -> None:
    """Render a lightweight page autoscroll control with speed presets."""
    enable_key = f"{scope_key}-autoscroll-enabled"
    speed_key = f"{scope_key}-autoscroll-speed"
    left, right = st.columns([1.4, 1])
    with left:
        enabled = st.toggle(
            "Auto-scroll",
            key=enable_key,
            help="Automatically move the page downward while you read.",
        )
    with right:
        speed_label = st.select_slider(
            "Speed",
            options=["0.5x", "1x", "1.5x", "2x", "2.5x", "3x"],
            value=st.session_state.get(speed_key, "1x"),
            key=speed_key,
        )
    st.caption(
        "Use auto-scroll while singing or reading through the chart. "
        "You can stop it any time."
    )
    _render_autoscroll_script(
        scope_key=scope_key,
        enabled=enabled,
        pixels_per_tick=_speed_to_pixels_per_tick(speed_label),
    )


def _render_autoscroll_script(
    *, scope_key: str, enabled: bool, pixels_per_tick: int
) -> None:
    """Inject an iframe script that scrolls the parent page."""
    active_flag = "true" if enabled else "false"
    components.html(
        f"""
        <script>
        const intervalKey = "snAutoscrollInterval_{scope_key}";
        const activeFlag = {active_flag};
        const step = {pixels_per_tick};
        const targetWindow = window.parent;
        if (targetWindow[intervalKey]) {{
          targetWindow.clearInterval(targetWindow[intervalKey]);
          targetWindow[intervalKey] = null;
        }}
        if (activeFlag) {{
          targetWindow[intervalKey] = targetWindow.setInterval(() => {{
            const doc = targetWindow.document.documentElement;
            const maxScroll = doc.scrollHeight - targetWindow.innerHeight;
            if (targetWindow.scrollY >= maxScroll) {{
              targetWindow.clearInterval(targetWindow[intervalKey]);
              targetWindow[intervalKey] = null;
              return;
            }}
            targetWindow.scrollBy({{ top: step, left: 0, behavior: "auto" }});
          }}, 80);
        }}
        </script>
        """,
        height=0,
        width=0,
    )


def _speed_to_pixels_per_tick(speed_label: str) -> int:
    """Map the visible speed choice to a scroll step size."""
    return {
        "0.5x": 1,
        "1x": 2,
        "1.5x": 3,
        "2x": 4,
        "2.5x": 5,
        "3x": 6,
    }[speed_label]


def _parse_note_sequence(notes_text: str) -> list[str]:
    """Split a note string into note tokens."""
    tokens = [
        token.strip()
        for token in re.split(r"[\s,]+", notes_text)
        if token.strip()
    ]
    if not tokens:
        raise ValueError("Enter at least one note.")
    return tokens


def _is_instrumental_segment(segment: LyricSegment) -> bool:
    """Return whether a lyric segment is only an instrumental placeholder."""
    return segment.text.strip().lower() == "(instrumental)"


def _should_render_melody_segment(segment: LyricSegment) -> bool:
    """Skip instrumental and empty melody rows in the melody tab."""
    return bool(segment.melody_packages) and not _is_instrumental_segment(
        segment
    )


def _update_melody_package(
    song: Song,
    *,
    segment_id: str,
    package_id: str,
    package_text: str,
    notes_text: str,
) -> None:
    """Update one melody package and validate the song."""
    text_value = package_text.strip()
    if not text_value:
        raise ValueError("Package text cannot be empty.")
    replacement_tokens = _parse_note_sequence(notes_text)
    segment = _find_segment(song, segment_id)
    package = next(
        (
            package
            for package in segment.melody_packages
            if package.id == package_id
        ),
        None,
    )
    if package is None:
        raise ValueError("Selected melody package could not be matched.")

    duration_template = [note.duration_beats for note in package.notes]
    package.text = text_value
    package.notes = [
        _parse_note_token(
            segment_id,
            token,
            _duration_for_index(duration_template, index),
            index,
        )
        for index, token in enumerate(replacement_tokens)
    ]
    _assign_validated_song(song)


def _insert_melody_package(
    song: Song,
    *,
    segment_id: str,
    anchor_package_id: str | None,
    position: str,
) -> None:
    """Insert a new melody package around an anchor package."""
    segment = _find_segment(song, segment_id)
    packages = sorted(
        segment.melody_packages,
        key=lambda package: package.order,
    )
    insert_at = len(packages)
    if anchor_package_id is not None:
        for index, package in enumerate(packages):
            if package.id == anchor_package_id:
                insert_at = index if position == "before" else index + 1
                break

    packages.insert(
        insert_at,
        MelodyPackage(
            id=_next_package_id(segment),
            text="New syllable",
            order=insert_at,
            notes=[
                MelodyNote(
                    segment_id=segment.id,
                    note="C",
                    octave=None,
                    duration_beats=1.0,
                    order=0,
                )
            ],
        ),
    )
    for index, package in enumerate(packages):
        package.order = index
    segment.melody_packages = packages
    _assign_validated_song(song)


def _delete_melody_package(
    song: Song,
    *,
    segment_id: str,
    package_id: str,
) -> None:
    """Delete one melody package from a lyric line."""
    segment = _find_segment(song, segment_id)
    segment.melody_packages = [
        package
        for package in segment.melody_packages
        if package.id != package_id
    ]
    for index, package in enumerate(segment.melody_packages):
        package.order = index
    _assign_validated_song(song)


def _find_segment(song: Song, segment_id: str) -> LyricSegment:
    """Return one lyric segment by id or raise a useful error."""
    for section in song.lyric_sections:
        for segment in section.segments:
            if segment.id == segment_id:
                return segment
    raise ValueError("Selected melody line could not be matched.")


def _next_package_id(segment: LyricSegment) -> str:
    """Return the next unique package id for a lyric segment."""
    existing_ids = {package.id for package in segment.melody_packages}
    next_index = 1
    while True:
        candidate = f"{segment.id}-pkg-{next_index}"
        if candidate not in existing_ids:
            return candidate
        next_index += 1


def _assign_validated_song(song: Song) -> None:
    """Re-validate and write canonical package-derived data back to the song."""
    validated = Song.model_validate(song.model_dump())
    song.lyric_sections = validated.lyric_sections
    song.melody_notes = validated.melody_notes


def _duration_for_index(duration_template: list[float], index: int) -> float:
    """Preserve existing durations when possible, else default to one beat."""
    if index < len(duration_template):
        return duration_template[index]
    return 1.0


def _chunked(items: list[T], size: int) -> list[list[T]]:
    """Split a list into fixed-size chunks."""
    return [items[index : index + size] for index in range(0, len(items), size)]


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
