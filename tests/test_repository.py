"""Tests for SQLite song persistence."""

from __future__ import annotations

from pathlib import Path

from singnote.storage.repository import (
    SQLiteSongRepository,
    create_engine_and_init,
)
from tests.support import build_sample_song


def test_repository_can_create_and_load_song(tmp_path: Path) -> None:
    """The repository should persist and load a structured song."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)
    song = build_sample_song()

    repository.upsert_song(song)
    loaded_song = repository.get_song(song.id)

    assert loaded_song is not None
    assert loaded_song.title == song.title
    assert loaded_song.key_signature == "G major"
    assert loaded_song.lyric_sections[0].segments[0].text == "So"
    assert loaded_song.melody_notes[0].segment_id == "seg-1"


def test_repository_can_update_existing_song(tmp_path: Path) -> None:
    """Upsert should replace the persisted payload for an existing song."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)
    song = build_sample_song()
    repository.upsert_song(song)

    updated_song = build_sample_song()
    updated_song.title = "Wish You Were Here (Lesson Edit)"
    updated_song.description = "Teacher updated the song title."
    repository.upsert_song(updated_song)

    loaded_song = repository.get_song(song.id)
    assert loaded_song is not None
    assert loaded_song.title == "Wish You Were Here (Lesson Edit)"
    assert loaded_song.description == "Teacher updated the song title."


def test_repository_seeds_only_missing_songs(tmp_path: Path) -> None:
    """Seed behavior should be idempotent for existing song ids."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)

    inserted_first = repository.seed_songs([build_sample_song()])
    inserted_second = repository.seed_songs([build_sample_song()])

    assert inserted_first == 1
    assert inserted_second == 0
    assert len(repository.list_songs()) == 1
