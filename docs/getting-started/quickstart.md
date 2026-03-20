# Quickstart

Get SingNote running locally with the active supported workflow.

Canonical sources:
- [`pyproject.toml`](../../pyproject.toml)
- [`streamlit_app.py`](../../streamlit_app.py)
- [`src/singnote/config.py`](../../src/singnote/config.py)

## Prerequisites

- Python 3.11, 3.12, or 3.13
- PowerShell 5.1 on Windows if you want commands to match the repo workflow

## Install

```powershell
pip install -e .[dev]
```

This installs:

- the `singnote` package from `src/singnote`
- Streamlit
- SQLModel and SQLAlchemy support
- PyYAML
- dev tools such as pytest, Ruff, and mypy

## Configure Shared Login

```powershell
$env:SINGNOTE_SHARED_USERNAME = "shared-teacher"
$env:SINGNOTE_SHARED_PASSWORD = "change-me-before-deploy"
```

Optional runtime override:

```powershell
$env:SINGNOTE_DATA_DIR = "instance"
```

If `SINGNOTE_DATA_DIR` is not set, the app uses `instance/`.

## Run

```powershell
python -m streamlit run streamlit_app.py
```

## First Successful Run

You should see:

- a login screen
- the seeded `Wish You Were Here` song card after login
- three tabs in the workspace:
  `Chords`, `Melody`, and `General`

The first run also creates a local SQLite database at `instance/singnote.db`
unless you changed `SINGNOTE_DATA_DIR`.

## Deployment Notes

On Streamlit Community Cloud, configure these secrets:

- `SINGNOTE_SHARED_USERNAME`
- `SINGNOTE_SHARED_PASSWORD`

Then point the deployment at:

- repo branch: `main`
- main file: `streamlit_app.py`
