"""Tests for application bootstrap and configuration."""

from __future__ import annotations

from pathlib import Path

from singnote.bootstrap import bootstrap_application
from singnote.config import load_settings


def test_load_settings_uses_default_instance_directory(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Defaults should target an instance database inside the data dir."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SINGNOTE_DATA_DIR", raising=False)
    monkeypatch.delenv("SINGNOTE_SHARED_USERNAME", raising=False)
    monkeypatch.delenv("SINGNOTE_SHARED_PASSWORD", raising=False)

    settings = load_settings()

    assert settings.app_name == "SingNote"
    assert settings.environment == "development"
    assert settings.data_dir == Path("instance")
    assert settings.database_path == Path("instance") / "singnote.db"
    assert settings.database_url.endswith("instance/singnote.db")
    assert settings.shared_username is None
    assert settings.shared_password is None


def test_load_settings_accepts_environment_overrides(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Explicit environment variables should override defaults."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SINGNOTE_ENV", "test")
    monkeypatch.setenv("SINGNOTE_DATA_DIR", str(tmp_path / "custom-data"))
    monkeypatch.setenv("SINGNOTE_SHARED_USERNAME", "teacher")
    monkeypatch.setenv("SINGNOTE_SHARED_PASSWORD", "teacher-pass")

    settings = load_settings()

    assert settings.environment == "test"
    assert settings.data_dir == tmp_path / "custom-data"
    assert settings.shared_username == "teacher"
    assert settings.shared_password == "teacher-pass"


def test_bootstrap_application_creates_seeded_database(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Bootstrap should prepare persistence and seed the sample song."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SINGNOTE_DATA_DIR", str(tmp_path / "runtime"))

    app = bootstrap_application()
    songs = app.repository.list_songs()

    assert app.settings.data_dir.exists()
    assert app.settings.database_path.exists()
    assert len(songs) == 1
    assert songs[0].title == "Wish You Were Here"
