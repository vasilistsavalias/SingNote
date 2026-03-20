# SingNote

SingNote is a mobile-first Streamlit app for teacher-student singing practice.
It keeps songs as reusable lesson cards with three coordinated tabs:

- lyrics plus chords
- melody dictation with grouped lyric-note packages
- rhythm, tempo, and coaching notes

The current MVP uses a shared username/password instead of full accounts and
stores songs in local SQLite.

## Features

- shared login gate for one teacher/student account
- manual song authoring with structured lyrics, chords, melody, rhythm, and notes
- seeded `Wish You Were Here` lesson card with chord functions and grouped melody packages
- in-place melody package editing through native mobile-friendly controls
- portable YAML song authoring for seed files and advanced editing
- mobile-first Streamlit styling with a responsive desktop layout

## Local Run

1. Create and activate a Python 3.11+ environment.
2. Install the project:

```bash
pip install -e .[dev]
```

3. Set the shared credentials:

```powershell
$env:SINGNOTE_SHARED_USERNAME = "shared-teacher"
$env:SINGNOTE_SHARED_PASSWORD = "change-me-before-deploy"
```

4. Start the app:

```bash
python -m streamlit run streamlit_app.py
```

## Data And Editing

- songs are stored in `instance/singnote.db` by default
- existing databases are migrated automatically when new song metadata fields are added
- seed songs now live under `seed_data/songs/`
- preferred seed format is portable YAML, though legacy JSON still loads
- add a new seed song by creating another `*.yaml` file in that directory
- the preferred schema is:
  `song` metadata, then `sections[].lines[]` with optional `chords`,
  `roman_numerals`, `melody_text` or `melody_packages`, `rhythm`, and
  `annotations`
- for fast melody authoring, prefer `melody_text: |` with one package per line,
  for example `So = C,B,G`
- `melody_packages[]` still works when you want explicit structured control
- Python loads and validates those files at startup, so you do not need a new
  Python file per song
- if a seed-managed song changes on disk, startup reseeding now refreshes that
  row automatically
- if you manually edit a seeded song inside the app, that row becomes
  user-managed and will not be overwritten by later seed refreshes
- use the sidebar `Settings` control to explicitly reset a song from its
  seed file if you want to discard in-app edits and resync it
- the authoring panel also exposes a portable YAML editor for advanced
  song editing without touching Python code

## Streamlit Community Cloud

For deployment, set these app secrets in Streamlit Community Cloud:

- `SINGNOTE_SHARED_USERNAME`
- `SINGNOTE_SHARED_PASSWORD`

The app also reads the same names from environment variables for local runs.

## Quality Checks

Run the local verification suite with:

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src
```
