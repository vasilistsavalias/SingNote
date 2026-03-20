"""Runtime configuration for SingNote."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
        shared_username=_setting_value("SINGNOTE_SHARED_USERNAME"),
        shared_password=_setting_value("SINGNOTE_SHARED_PASSWORD"),
    )


def _setting_value(name: str) -> str | None:
    """Read a setting from environment first, then Streamlit secrets."""
    environment_value = os.getenv(name)
    if environment_value is not None:
        return environment_value
    return _secret_value(name)


def _secret_value(name: str) -> str | None:
    """Read a secret without requiring local secret files in development."""
    try:
        import streamlit as st
    except Exception:
        return None

    try:
        value: Any = st.secrets.get(name)
    except Exception:
        return None

    if value is None:
        return None
    return str(value)
