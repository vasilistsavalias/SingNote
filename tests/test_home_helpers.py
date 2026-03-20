"""Tests for home-page helper behavior."""

from __future__ import annotations

import pytest

from singnote.ui.home import (
    _delete_melody_package,
    _favicon_head_script,
    _format_package_note_sequence,
    _format_segment_melody_text,
    _insert_melody_package,
    _is_instrumental_segment,
    _lyrics_sheet_markup,
    _melody_reader_markup,
    _melody_sheet_line_markup,
    _parse_melody_text_lines,
    _parse_note_sequence,
    _parse_note_token,
    _replace_melody_line,
    _self_scroll_component_html,
    _should_render_melody_segment,
    _speed_to_pixels_per_second,
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


def test_parse_melody_text_lines_accepts_shorthand() -> None:
    """Whole-line editor should parse shorthand melody package lines."""
    parsed_lines = _parse_melody_text_lines("So = C,B,G\nthink => C")

    assert parsed_lines == [("So", ["C", "B", "G"]), ("think", ["C"])]


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


def test_replace_melody_line_updates_lyrics_and_packages() -> None:
    """Whole-line edit should replace segment text and packages together."""
    song = build_sample_song()

    _replace_melody_line(
        song,
        segment_id="seg-1",
        lyric_text="So, so",
        melody_text="So = C,B,G\nso = A",
    )

    segment = song.lyric_sections[0].segments[0]
    assert segment.text == "So, so"
    assert [package.text for package in segment.melody_packages] == [
        "So",
        "so",
    ]
    assert [note.note for note in segment.melody_packages[0].notes] == [
        "C",
        "B",
        "G",
    ]


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


def test_lyrics_sheet_markup_keeps_lyric_text_visible() -> None:
    """Chords tab should still show the lyric text under the chords."""
    markup = _lyrics_sheet_markup(build_sample_song())

    assert "So you think" in markup
    assert 'class="sn-sheet-lyric"' in markup


def test_melody_sheet_line_markup_renders_inline_packages() -> None:
    """Melody tab should render one line as inline note-over-word packages."""
    segment = build_sample_song().lyric_sections[0].segments[0]

    markup = _melody_sheet_line_markup(segment)

    assert 'class="sn-melody-line-shell"' in markup
    assert 'class="sn-melody-inline-package"' in markup
    assert 'class="sn-melody-inline-notes"' in markup
    assert 'class="sn-melody-inline-text"' in markup


def test_melody_reader_markup_wraps_sections_in_song_sheet() -> None:
    """Melody reader mode should render a full sheet for iframe playback."""
    markup = _melody_reader_markup(build_sample_song())

    assert 'class="sn-song-sheet sn-song-sheet-melody-reader"' in markup
    assert 'class="sn-sheet-section-title"' in markup
    assert 'class="sn-melody-line-shell"' in markup


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


def test_speed_to_pixels_per_second_covers_visible_presets() -> None:
    """Reader speeds should map to stable pixels-per-second values."""
    assert _speed_to_pixels_per_second("0.1x") == 3
    assert _speed_to_pixels_per_second("0.5x") == 15
    assert _speed_to_pixels_per_second("1x") == 30
    assert _speed_to_pixels_per_second("1.1x") == 33
    assert _speed_to_pixels_per_second("1.5x") == 45
    assert _speed_to_pixels_per_second("2x") == 60
    assert _speed_to_pixels_per_second("2.5x") == 75
    assert _speed_to_pixels_per_second("3x") == 90


def test_self_scroll_component_html_is_self_contained() -> None:
    """The robust reader should scroll its own internal container only."""
    html = _self_scroll_component_html(
        content_html="<div>Reader body</div>",
        is_playing=True,
        pixels_per_second=30,
        height=520,
        scope_key="chords-song-1",
    )

    assert 'id="scroll-container"' in html
    assert "window.parent" not in html
    assert "setInterval" in html
    assert "Reader body" in html
    assert 'data-scope="chords-song-1"' in html


def test_self_scroll_component_html_starts_only_when_playing() -> None:
    """Baked reader state should control whether auto-scroll starts."""
    html = _self_scroll_component_html(
        content_html="<div>Reader body</div>",
        is_playing=False,
        pixels_per_second=60,
        height=520,
        scope_key="chords-song-2",
    )

    assert "const IS_PLAYING = false;" in html
    assert "setTimeout(startScroll, 120);" in html


def test_favicon_head_script_points_to_static_assets() -> None:
    """Favicon head injection should reference the static favicon pack."""
    script = _favicon_head_script()

    assert "/app/static/apple-touch-icon.png" in script
    assert "/app/static/favicon-32x32.png" in script
    assert "/app/static/favicon-16x16.png" in script
    assert "/app/static/site.webmanifest" in script


def test_format_segment_melody_text_uses_editable_shorthand() -> None:
    """Existing package data should serialize back into whole-line shorthand."""
    segment = build_sample_song().lyric_sections[0].segments[0]

    shorthand = _format_segment_melody_text(segment)

    assert "So = E4" in shorthand
