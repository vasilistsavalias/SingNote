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
    if environment_value is not None and environment_value not in (
        "shared-teacher",
        "change-me-before-deploy",
    ):
        return environment_value

    secret = _secret_value(name)
    if secret is not None:
        return secret

    if environment_value is not None:
        return environment_value

    return None


def _secret_value(name: str) -> str | None:
    """Read a secret without requiring local secret files in development."""
    short_name = name.removeprefix("SINGNOTE_SHARED_").lower()
    try:
        import streamlit as st

        value: Any = st.secrets.get(name)
        if value is None:
            value = st.secrets.get(short_name)
        if value is not None:
            return str(value)
    except Exception:
        pass

    secrets_path = Path(".streamlit") / "secrets.toml"
    if secrets_path.exists():
        try:
            import tomllib

            with secrets_path.open("rb") as f:
                data = tomllib.load(f)
                val = data.get(name)
                if val is None:
                    val = data.get(short_name)
                if val is not None:
                    return str(val)
        except Exception:
            pass

    return None
