"""SQLite-backed persistence models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class SongRecord(SQLModel, table=True):
    """Persisted song payload stored in JSON columns for MVP simplicity."""

    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    title: str
    artist: str | None = None
    description: str | None = None
    key_signature: str | None = None
    time_signature: str | None = None
    tempo_bpm: int | None = None
    tempo_notes: str | None = None
    strumming_pattern: str | None = None
    lyric_sections: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    chord_events: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    melody_notes: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    rhythm_cues: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    teacher_annotations: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    is_seed_managed: bool = Field(default=False, nullable=False)
    seed_signature: str | None = None
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
