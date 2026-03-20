"""Repository layer for storing and loading songs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from singnote.domain.models import Song
from singnote.storage.models import SongRecord


def create_engine_and_init(database_url: str) -> Engine:
    """Create the SQLAlchemy engine and initialize schema."""
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    return engine


class SQLiteSongRepository:
    """Repository for CRUD operations on songs."""

    def __init__(self, engine: Engine):
        self._engine = engine

    def upsert_song(self, song: Song) -> Song:
        """Create or replace a song record."""
        payload = self._to_record(song)
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
        """Insert songs that do not already exist."""
        inserted = 0
        with Session(self._engine) as session:
            for song in songs:
                if session.get(SongRecord, song.id) is not None:
                    continue
                record = self._to_record(song)
                now = _utc_now()
                record.created_at = now
                record.updated_at = now
                session.add(record)
                inserted += 1
            session.commit()
        return inserted

    @staticmethod
    def _to_record(song: Song) -> SongRecord:
        """Convert a domain song into a persisted record."""
        return SongRecord(
            id=song.id,
            title=song.title,
            artist=song.artist,
            description=song.description,
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
                "lyric_sections": record.lyric_sections,
                "chord_events": record.chord_events,
                "melody_notes": record.melody_notes,
                "rhythm_cues": record.rhythm_cues,
                "teacher_annotations": record.teacher_annotations,
            }
        )


def _utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)
