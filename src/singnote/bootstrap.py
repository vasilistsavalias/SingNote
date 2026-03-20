"""Application bootstrap utilities."""

from __future__ import annotations

from dataclasses import dataclass

from singnote.config import Settings, load_settings
from singnote.seeds import build_sample_songs
from singnote.storage.repository import (
    SQLiteSongRepository,
    create_engine_and_init,
)


@dataclass
class Application:
    """Bootstrapped application context."""

    settings: Settings
    repository: SQLiteSongRepository

    def render(self) -> None:
        """Render the root Streamlit application."""
        from singnote.ui.home import render_home_page

        render_home_page(self)


def bootstrap_application() -> Application:
    """Prepare directories, persistence, and UI dependencies."""
    settings = load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine_and_init(settings.database_url)
    repository = SQLiteSongRepository(engine)
    repository.seed_songs(build_sample_songs())
    return Application(settings=settings, repository=repository)
