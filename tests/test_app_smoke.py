"""End-to-end-ish smoke tests for the Streamlit app."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_login_and_seeded_song_workspace(
    monkeypatch,
    tmp_path,
) -> None:
    """The shared login should unlock the seeded song workspace."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SINGNOTE_DATA_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("SINGNOTE_SHARED_USERNAME", "shared-teacher")
    monkeypatch.setenv(
        "SINGNOTE_SHARED_PASSWORD",
        "change-me-before-deploy",
    )

    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    app = AppTest.from_file(str(app_path))
    app.run()

    assert [title.value for title in app.title] == ["SingNote Login"]
    assert [field.label for field in app.text_input] == [
        "Username",
        "Password",
    ]

    app.text_input[0].input("shared-teacher")
    app.text_input[1].input("change-me-before-deploy")
    app.button[0].click()
    app.run()

    assert "Song Catalog" in [subheader.value for subheader in app.subheader]
    assert "Wish You Were Here" in [
        subheader.value for subheader in app.subheader
    ]
    assert any(
        "G major" in caption.value
        for caption in app.caption
        if isinstance(caption.value, str)
    )
