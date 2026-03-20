# Artifacts

This page lists the main runtime and source artifacts.

Canonical sources:
- [`src/singnote/config.py`](../../src/singnote/config.py)
- [`seed_data/songs/`](../../seed_data/songs)

## Source Artifacts

- `seed_data/songs/*.yaml`
  Active portable seed song format
- `seed_data/songs/*.json`
  Legacy portable seed song format, still supported
- `src/singnote/`
  Application source code
- `tests/`
  Verification suite

## Runtime Artifacts

- `instance/singnote.db`
  Default SQLite database
- `.streamlit/config.toml`
  Streamlit config used by local/dev deployment

## Local-Only Project Artifacts

- `conductor/`
  Local planning and execution artifacts, not meant for git history
- `.codex/`
  Local agent skills and support files

## Output Model

The app does not currently generate reports, exports, or build artifacts beyond:

- the local SQLite database
- cached Python/test tooling artifacts
