"""Repository layer for storing and loading songs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from singnote.domain.models import Song
from singnote.storage.models import SongRecord


def create_engine_and_init(database_url: str) -> Engine:
    """Create the SQLAlchemy engine and initialize schema."""
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    _migrate_song_record_schema(engine)
    return engine


class SQLiteSongRepository:
    """Repository for CRUD operations on songs."""

    def __init__(self, engine: Engine):
        self._engine = engine

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
