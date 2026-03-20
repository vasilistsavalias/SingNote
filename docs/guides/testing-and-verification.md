# Testing And Verification

This page summarizes the active verification workflow for SingNote.

Canonical sources:
- [`pyproject.toml`](../../pyproject.toml)
- [`tests/`](../../tests)

## Primary Commands

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy src
```

## What The Tests Cover

- login flow and seeded app smoke path
- seed loading and portable YAML parsing
- authoring helpers
- domain model validation
- repository persistence and reseeding behavior
- UI helper functions
- bootstrap behavior

## Manual Verification

For changes that affect the visual app:

1. run the Streamlit app locally
2. log in with the shared credentials
3. open the seeded song
4. verify the relevant tab behavior
5. if you changed seed YAML for a seed-managed song, restart the app
6. if the song was manually edited before, recreate the local database first

## Deployment Verification

For Streamlit Community Cloud:

1. push to `main`
2. reboot or redeploy the app
3. log in
4. confirm the current seed data appears
5. verify the `Chords`, `Melody`, and `General` tabs reflect the new build
