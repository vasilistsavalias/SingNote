"""Tests for home-page helper behavior."""

from __future__ import annotations

import pytest

from singnote.ui.home import (
    _autoscroll_script,
    _delete_melody_package,
    _favicon_head_script,
    _format_package_note_sequence,
    _insert_melody_package,
    _is_instrumental_segment,
    _lyrics_sheet_markup,
    _parse_note_sequence,
    _parse_note_token,
    _should_render_melody_segment,
    _speed_to_pixels_per_tick,
    _update_melody_package,
)
from tests.support import build_sample_song


def test_parse_note_token_accepts_sharp_notes() -> None:
    """Inline note edits should accept note tokens like F#4."""
    note = _parse_note_token("seg-1", "F#4", 1.5)

    assert note.segment_id == "seg-1"
    assert note.note == "F#"
    assert note.octave == 4
    assert note.duration_beats == 1.5


def test_parse_note_token_rejects_invalid_tokens() -> None:
    """Inline note edits should reject malformed note labels."""
    with pytest.raises(ValueError):
        _parse_note_token("seg-1", "middle-c", 1.0)


def test_format_package_note_sequence_is_readable() -> None:
    """Melody packages should render as one readable note string."""
    package = (
        build_sample_song().lyric_sections[0].segments[0].melody_packages[0]
    )

    assert _format_package_note_sequence(package) == "E4"


def test_parse_note_sequence_accepts_commas_and_spaces() -> None:
    """Line editing should accept either comma- or space-separated notes."""
    notes = _parse_note_sequence("C, B G, A")

    assert notes == ["C", "B", "G", "A"]


def test_update_melody_package_replaces_package_text_and_notes() -> None:
    """A package edit should update the matching melody package."""
    song = build_sample_song()

    _update_melody_package(
        song,
        segment_id="seg-2",
        package_id="seg-2-pkg-1",
        package_text="youuu",
        notes_text="A4 C5",
    )

    updated_package = song.lyric_sections[0].segments[1].melody_packages[0]
    updated_notes = [
        note for note in song.melody_notes if note.segment_id == "seg-2"
    ]
    assert updated_package.text == "youuu"
    assert len(updated_notes) == 2
    assert updated_notes[0].note == "A"
    assert updated_notes[0].octave == 4
    assert updated_notes[0].duration_beats == 1.0
    assert updated_notes[1].note == "C"
    assert updated_notes[1].octave == 5


def test_update_melody_package_rejects_unknown_segment_ids() -> None:
    """Package updates should fail for missing segment ids."""
    song = build_sample_song()

    with pytest.raises(ValueError):
        _update_melody_package(
            song,
            segment_id="missing",
            package_id="seg-2-pkg-1",
            package_text="missing",
            notes_text="A4",
        )


def test_insert_melody_package_adds_new_package_after_anchor() -> None:
    """Package insertion should preserve package ordering."""
    song = build_sample_song()

    _insert_melody_package(
        song,
        segment_id="seg-1",
        anchor_package_id="seg-1-pkg-1",
        position="after",
    )

    packages = song.lyric_sections[0].segments[0].melody_packages
    assert len(packages) == 3
    assert packages[1].id == "seg-1-pkg-3"
    assert packages[1].text == "New syllable"


def test_delete_melody_package_removes_selected_package() -> None:
    """Package deletion should remove only the selected melody package."""
    song = build_sample_song()

    _delete_melody_package(
        song,
        segment_id="seg-1",
        package_id="seg-1-pkg-1",
    )

    packages = song.lyric_sections[0].segments[0].melody_packages
    assert len(packages) == 1
    assert packages[0].id == "seg-1-pkg-2"


def test_lyrics_sheet_markup_reads_like_one_chart() -> None:
    """Lyrics tab markup should render as one coherent song sheet."""
    markup = _lyrics_sheet_markup(build_sample_song())

    assert 'class="sn-song-sheet"' in markup
    assert 'class="sn-sheet-section-title"' in markup
    assert 'class="sn-sheet-chords"' in markup
    assert 'class="sn-sheet-lyric"' in markup


def test_lyrics_sheet_markup_skips_instrumental_placeholders() -> None:
    """Instrumental placeholder lines should not appear in the lyrics chart."""
    song = build_sample_song()
    song.lyric_sections[0].segments[0].text = "(instrumental)"

    markup = _lyrics_sheet_markup(song)

    assert "(instrumental)" not in markup


def test_should_render_melody_segment_skips_empty_instrumentals() -> None:
    """Melody tab should skip placeholder rows without melody packages."""
    segment = build_sample_song().lyric_sections[0].segments[0]
    segment.text = "(instrumental)"
    segment.melody_packages = []

    assert _is_instrumental_segment(segment) is True
    assert _should_render_melody_segment(segment) is False


def test_speed_to_pixels_per_tick_covers_visible_presets() -> None:
    """Auto-scroll speeds should map to stable scroll steps."""
    assert _speed_to_pixels_per_tick("0.5x") == 1
    assert _speed_to_pixels_per_tick("1x") == 2
    assert _speed_to_pixels_per_tick("1.5x") == 3
    assert _speed_to_pixels_per_tick("2x") == 4
    assert _speed_to_pixels_per_tick("2.5x") == 5
    assert _speed_to_pixels_per_tick("3x") == 6


def test_autoscroll_script_targets_streamlit_scroll_container() -> None:
    """Auto-scroll should search the app container, not only window scroll."""
    script = _autoscroll_script(
        scope_key="lyrics",
        enabled=True,
        pixels_per_tick=4,
    )

    assert 'data-testid="stAppViewContainer"' in script
    assert "scrollTop" in script
    assert "requestAnimationFrame" in script


def test_autoscroll_script_respects_disabled_state() -> None:
    """Disabled auto-scroll should tear down the loop and stop."""
    script = _autoscroll_script(
        scope_key="melody",
        enabled=False,
        pixels_per_tick=2,
    )

    assert "if (!activeFlag)" in script
    assert "cancelLoop();" in script


def test_favicon_head_script_points_to_static_assets() -> None:
    """Favicon head injection should reference the static favicon pack."""
    script = _favicon_head_script()

    assert "/app/static/apple-touch-icon.png" in script
    assert "/app/static/favicon-32x32.png" in script
    assert "/app/static/favicon-16x16.png" in script
    assert "/app/static/site.webmanifest" in script
