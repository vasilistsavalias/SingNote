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
    """Seeding the same managed payload twice should be idempotent."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)

    inserted_first = repository.seed_songs([build_sample_song()])
    inserted_second = repository.seed_songs([build_sample_song()])

    assert inserted_first == 1
    assert inserted_second == 0
    assert len(repository.list_songs()) == 1


def test_repository_refreshes_changed_seed_song(tmp_path: Path) -> None:
    """Managed seed rows should refresh when the JSON payload changes."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)

    repository.seed_songs([build_sample_song()])
    updated_seed = build_sample_song()
    updated_seed.description = "Refreshed from seed json."

    inserted = repository.seed_songs([updated_seed])
    loaded_song = repository.get_song(updated_seed.id)

    assert inserted == 1
    assert loaded_song is not None
    assert loaded_song.description == "Refreshed from seed json."


def test_repository_does_not_overwrite_manual_song_edits(
    tmp_path: Path,
) -> None:
    """Manual edits should opt a song out of automatic seed refreshes."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)

    repository.seed_songs([build_sample_song()])
    manual_edit = build_sample_song()
    manual_edit.title = "Teacher Version"
    repository.upsert_song(manual_edit)

    refreshed_seed = build_sample_song()
    refreshed_seed.description = "Seed changed on disk."
    inserted = repository.seed_songs([refreshed_seed])
    loaded_song = repository.get_song(refreshed_seed.id)

    assert inserted == 0
    assert loaded_song is not None
    assert loaded_song.title == "Teacher Version"


def test_repository_can_reset_manual_song_back_to_seed(
    tmp_path: Path,
) -> None:
    """Explicit reset should restore the latest seed-managed payload."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine)

    original_seed = build_sample_song()
    repository.seed_songs([original_seed])

    manual_edit = build_sample_song()
    manual_edit.title = "Teacher Version"
    repository.upsert_song(manual_edit)

    refreshed_seed = build_sample_song()
    refreshed_seed.description = "Reset from JSON seed."
    repository.reset_song_to_seed(refreshed_seed)
    loaded_song = repository.get_song(refreshed_seed.id)

    assert loaded_song is not None
    assert loaded_song.title == "Wish You Were Here"
    assert loaded_song.description == "Reset from JSON seed."
