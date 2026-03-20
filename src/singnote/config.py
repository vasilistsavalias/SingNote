"""Runtime configuration for SingNote."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Application settings derived from environment variables."""

    app_name: str
    environment: str
    data_dir: Path
    database_path: Path
    database_url: str
    shared_username: str | None
    shared_password: str | None


def load_settings() -> Settings:
    """Load application settings from environment variables."""
    data_dir = Path(os.getenv("SINGNOTE_DATA_DIR", "instance"))
    database_path = data_dir / "singnote.db"
    return Settings(
        app_name="SingNote",
        environment=os.getenv("SINGNOTE_ENV", "development"),
        data_dir=data_dir,
        database_path=database_path,
        database_url=f"sqlite:///{database_path.as_posix()}",
        shared_username=os.getenv("SINGNOTE_SHARED_USERNAME"),
        shared_password=os.getenv("SINGNOTE_SHARED_PASSWORD"),
    )
