"""Tests for SQLite song persistence."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect

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
    assert loaded_song.lyric_sections[0].segments[0].text == "So you think"
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


def test_repository_creates_recording_table_on_init(tmp_path: Path) -> None:
    """Schema initialization should include the recordings table."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)

    assert "recordingrecord" in inspect(engine).get_table_names()


def test_repository_can_create_list_and_load_recordings(
    tmp_path: Path,
) -> None:
    """Recordings should attach to one song and persist audio files."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    recordings_dir = tmp_path / "recordings"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(engine, recordings_dir=recordings_dir)
    song = build_sample_song()
    repository.upsert_song(song)

    first = repository.create_recording(
        song_id=song.id,
        title="Lesson take 1",
        original_filename="take-one.m4a",
        content_type="audio/mp4",
        file_bytes=b"fake-audio-one",
    )
    second = repository.create_recording(
        song_id=song.id,
        title="Lesson take 2",
        original_filename="take-two.wav",
        content_type="audio/wav",
        file_bytes=b"fake-audio-two",
    )

    recordings = repository.list_recordings_for_song(song.id)
    loaded = repository.get_recording(first.id)

    assert [recording.id for recording in recordings] == [
        second.id,
        first.id,
    ]
    assert loaded is not None
    assert loaded.title == "Lesson take 1"
    assert repository.recording_file_path(first).read_bytes() == (
        b"fake-audio-one"
    )


def test_repository_keeps_recordings_scoped_by_song(tmp_path: Path) -> None:
    """Recordings for one song should not leak into another song card."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(
        engine,
        recordings_dir=tmp_path / "recordings",
    )

    repository.create_recording(
        song_id="song-a",
        title="Song A take",
        original_filename="a.mp3",
        content_type="audio/mpeg",
        file_bytes=b"a",
    )
    repository.create_recording(
        song_id="song-b",
        title="Song B take",
        original_filename="b.mp3",
        content_type="audio/mpeg",
        file_bytes=b"b",
    )

    assert len(repository.list_recordings_for_song("song-a")) == 1
    assert repository.list_recordings_for_song("song-a")[0].title == (
        "Song A take"
    )


def test_repository_updates_recording_review(tmp_path: Path) -> None:
    """Structured evaluation fields should be editable."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(
        engine,
        recordings_dir=tmp_path / "recordings",
    )
    recording = repository.create_recording(
        song_id="song-a",
        title="Raw take",
        original_filename="take.mp3",
        content_type="audio/mpeg",
        file_bytes=b"audio",
    )

    updated = repository.update_recording_review(
        recording_id=recording.id,
        title="Reviewed take",
        status="Reviewed",
        teacher_notes="Better vowels.",
        student_notes="Felt easier.",
        next_steps="Repeat chorus.",
        pitch_notes="Watch the high note.",
        rhythm_notes="Do not rush.",
        breath_notes="Lower breath.",
    )

    assert updated is not None
    assert updated.title == "Reviewed take"
    assert updated.status == "Reviewed"
    assert updated.teacher_notes == "Better vowels."
    assert updated.next_steps == "Repeat chorus."


def test_repository_deletes_recording_when_file_is_missing(
    tmp_path: Path,
) -> None:
    """Metadata deletion should still work if the audio file disappeared."""
    database_url = f"sqlite:///{(tmp_path / 'songs.db').as_posix()}"
    engine = create_engine_and_init(database_url)
    repository = SQLiteSongRepository(
        engine,
        recordings_dir=tmp_path / "recordings",
    )
    recording = repository.create_recording(
        song_id="song-a",
        title="Delete me",
        original_filename="take.ogg",
        content_type="audio/ogg",
        file_bytes=b"audio",
    )
    repository.recording_file_path(recording).unlink()

    deleted = repository.delete_recording(recording.id)

    assert deleted is True
    assert repository.get_recording(recording.id) is None
