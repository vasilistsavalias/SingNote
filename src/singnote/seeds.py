"""JSON-backed seed song loading for SingNote."""

from __future__ import annotations

import json
from pathlib import Path

from singnote.domain.models import Song

SEED_SONGS_DIR = Path(__file__).resolve().parents[2] / "seed_data" / "songs"


def build_sample_songs(seed_songs_dir: Path | None = None) -> list[Song]:
    """Load seed songs from JSON files."""
    songs_dir = seed_songs_dir or SEED_SONGS_DIR
    if not songs_dir.exists():
        return []

    songs = [
        _load_song_file(path)
        for path in sorted(songs_dir.glob("*.json"))
    ]
    return songs


def _load_song_file(path: Path) -> Song:
    """Load one seed song file into a validated domain model."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Song.model_validate(payload)
