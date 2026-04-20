"""Repository layer for storing and loading songs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from singnote.domain.models import Song
from singnote.storage.models import RecordingRecord, SongRecord


def create_engine_and_init(database_url: str) -> Engine:
    """Create the SQLAlchemy engine and initialize schema."""
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    _migrate_song_record_schema(engine)
    return engine


class SQLiteSongRepository:
    """Repository for CRUD operations on songs."""

    def __init__(
        self,
        engine: Engine,
        recordings_dir: Path | str | None = None,
    ):
        self._engine = engine
        self._recordings_dir = Path(recordings_dir or "instance/recordings")

    def upsert_song(self, song: Song) -> Song:
        """Create or replace a song record."""
        payload = self._to_record(song, is_seed_managed=False)
        with Session(self._engine) as session:
            existing = session.get(SongRecord, song.id)
            if existing is None:
                payload.created_at = _utc_now()
            else:
                payload.created_at = existing.created_at
                session.delete(existing)
                session.flush()
            payload.updated_at = _utc_now()
            session.add(payload)
            session.commit()
        return song

    def get_song(self, song_id: str) -> Song | None:
        """Return a song by identifier."""
        with Session(self._engine) as session:
            record = session.get(SongRecord, song_id)
            return None if record is None else self._to_domain(record)

    def list_songs(self) -> list[Song]:
        """Return all songs ordered by title."""
        with Session(self._engine) as session:
            statement = select(SongRecord).order_by(SongRecord.title)
            records = session.exec(statement).all()
            return [self._to_domain(record) for record in records]

    def seed_songs(self, songs: list[Song]) -> int:
        """Insert new seed songs and refresh unchanged seed-managed records."""
        inserted = 0
        with Session(self._engine) as session:
            for song in songs:
                existing = session.get(SongRecord, song.id)
                signature = _song_signature(song)
                if existing is not None and not _should_refresh_seed(
                    existing, signature
                ):
                    continue
                record = self._to_record(
                    song,
                    is_seed_managed=True,
                    seed_signature=signature,
                )
                now = _utc_now()
                if existing is None:
                    record.created_at = now
                else:
                    record.created_at = existing.created_at
                    session.delete(existing)
                    session.flush()
                record.updated_at = now
                session.add(record)
                inserted += 1
            session.commit()
        return inserted

    def reset_song_to_seed(self, song: Song) -> Song:
        """Replace any existing row with the current seed-managed payload."""
        record = self._to_record(
            song,
            is_seed_managed=True,
            seed_signature=_song_signature(song),
        )
        with Session(self._engine) as session:
            existing = session.get(SongRecord, song.id)
            if existing is None:
                record.created_at = _utc_now()
            else:
                record.created_at = existing.created_at
                session.delete(existing)
                session.flush()
            record.updated_at = _utc_now()
            session.add(record)
            session.commit()
        return song

    def create_recording(
        self,
        *,
        song_id: str,
        title: str,
        original_filename: str,
        content_type: str | None,
        file_bytes: bytes,
        recorded_at: datetime | None = None,
    ) -> RecordingRecord:
        """Persist an uploaded recording file and its metadata."""
        recording_id = uuid4().hex
        safe_original_filename = Path(original_filename).name
        extension = Path(safe_original_filename).suffix.lower()
        stored_filename = f"{recording_id}{extension}"
        song_recordings_dir = self._recordings_dir / song_id
        file_path = song_recordings_dir / stored_filename
        song_recordings_dir.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(file_bytes)

        record = RecordingRecord(
            id=recording_id,
            song_id=song_id,
            title=title.strip() or Path(safe_original_filename).stem,
            original_filename=safe_original_filename,
            stored_filename=stored_filename,
            content_type=content_type,
            file_size_bytes=len(file_bytes),
            recorded_at=recorded_at,
        )
        try:
            with Session(self._engine) as session:
                session.add(record)
                session.commit()
                session.refresh(record)
        except Exception:
            file_path.unlink(missing_ok=True)
            raise
        return record

    def list_recordings_for_song(self, song_id: str) -> list[RecordingRecord]:
        """Return recordings for a song, newest first."""
        with Session(self._engine) as session:
            statement = (
                select(RecordingRecord)
                .where(RecordingRecord.song_id == song_id)
                .order_by(text("created_at DESC"))
            )
            return list(session.exec(statement).all())

    def get_recording(self, recording_id: str) -> RecordingRecord | None:
        """Return one recording by id."""
        with Session(self._engine) as session:
            return session.get(RecordingRecord, recording_id)

    def update_recording_review(
        self,
        *,
        recording_id: str,
        title: str,
        status: str,
        teacher_notes: str,
        student_notes: str,
        next_steps: str,
        pitch_notes: str,
        rhythm_notes: str,
        breath_notes: str,
    ) -> RecordingRecord | None:
        """Update human evaluation fields for one recording."""
        with Session(self._engine) as session:
            record = session.get(RecordingRecord, recording_id)
            if record is None:
                return None
            record.title = title.strip() or record.title
            record.status = status
            record.teacher_notes = teacher_notes
            record.student_notes = student_notes
            record.next_steps = next_steps
            record.pitch_notes = pitch_notes
            record.rhythm_notes = rhythm_notes
            record.breath_notes = breath_notes
            record.updated_at = _utc_now()
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def delete_recording(self, recording_id: str) -> bool:
        """Delete one recording row and best-effort delete its audio file."""
        with Session(self._engine) as session:
            record = session.get(RecordingRecord, recording_id)
            if record is None:
                return False
            file_path = self.recording_file_path(record)
            session.delete(record)
            session.commit()
        file_path.unlink(missing_ok=True)
        return True

    def recording_file_path(self, record: RecordingRecord) -> Path:
        """Return the local audio path for a recording record."""
        return self._recordings_dir / record.song_id / record.stored_filename

    @staticmethod
    def _to_record(
        song: Song,
        *,
        is_seed_managed: bool,
        seed_signature: str | None = None,
    ) -> SongRecord:
        """Convert a domain song into a persisted record."""
        return SongRecord(
            id=song.id,
            title=song.title,
            artist=song.artist,
            description=song.description,
            key_signature=song.key_signature,
            time_signature=song.time_signature,
            tempo_bpm=song.tempo_bpm,
            tempo_notes=song.tempo_notes,
            strumming_pattern=song.strumming_pattern,
            lyric_sections=[
                section.model_dump(mode="json")
                for section in song.lyric_sections
            ],
            chord_events=[
                event.model_dump(mode="json") for event in song.chord_events
            ],
            melody_notes=[
                note.model_dump(mode="json") for note in song.melody_notes
            ],
            rhythm_cues=[
                cue.model_dump(mode="json") for cue in song.rhythm_cues
            ],
            teacher_annotations=[
                annotation.model_dump(mode="json")
                for annotation in song.teacher_annotations
            ],
            is_seed_managed=is_seed_managed,
            seed_signature=seed_signature,
        )

    @staticmethod
    def _to_domain(record: SongRecord) -> Song:
        """Convert a persisted record into a validated domain song."""
        return Song.model_validate(
            {
                "id": record.id,
                "title": record.title,
                "artist": record.artist,
                "description": record.description,
                "key_signature": record.key_signature,
                "time_signature": record.time_signature,
                "tempo_bpm": record.tempo_bpm,
                "tempo_notes": record.tempo_notes,
                "strumming_pattern": record.strumming_pattern,
                "lyric_sections": record.lyric_sections,
                "chord_events": record.chord_events,
                "melody_notes": record.melody_notes,
                "rhythm_cues": record.rhythm_cues,
                "teacher_annotations": record.teacher_annotations,
            }
        )


def _migrate_song_record_schema(engine: Engine) -> None:
    """Add missing MVP metadata columns for older local databases."""
    table_name = str(SongRecord.__tablename__)
    existing_columns = {
        column["name"] for column in inspect(engine).get_columns(table_name)
    }
    required_columns = {
        "key_signature": "TEXT",
        "time_signature": "TEXT",
        "tempo_bpm": "INTEGER",
        "tempo_notes": "TEXT",
        "strumming_pattern": "TEXT",
        "is_seed_managed": "BOOLEAN NOT NULL DEFAULT 0",
        "seed_signature": "TEXT",
    }
    with engine.begin() as connection:
        for column_name, column_type in required_columns.items():
            if column_name in existing_columns:
                continue
            connection.execute(
                text(
                    f"ALTER TABLE {table_name} "
                    f"ADD COLUMN {column_name} {column_type}"
                )
            )


def _should_refresh_seed(
    existing: SongRecord, incoming_signature: str
) -> bool:
    """Refresh unchanged seed-managed rows when the seed payload changes."""
    return (
        existing.is_seed_managed
        and existing.seed_signature != incoming_signature
    )


def _song_signature(song: Song) -> str:
    """Return a stable signature for a canonical song payload."""
    canonical_payload = json.dumps(
        song.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)
