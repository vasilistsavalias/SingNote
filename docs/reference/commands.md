# Commands

This page is a lookup reference for commands that exist in the repository
today.

Canonical sources:
- [`README.md`](../../README.md)
- [`pyproject.toml`](../../pyproject.toml)

## Install

```powershell
pip install -e .[dev]
```

## Run The App

```powershell
python -m streamlit run streamlit_app.py
```

## Test

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy src
```

## Useful Environment Variables

```powershell
$env:SINGNOTE_SHARED_USERNAME = "shared-teacher"
$env:SINGNOTE_SHARED_PASSWORD = "change-me-before-deploy"
$env:SINGNOTE_DATA_DIR = "instance"
```

## Notes

- There is no deploy CLI for Streamlit Community Cloud in this repository.
- Deployment is configured from the Streamlit web UI.
