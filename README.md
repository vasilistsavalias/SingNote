# SingNote

SingNote is a mobile-first Streamlit app for teacher-student singing practice.
It keeps songs as reusable lesson cards with three coordinated tabs:

- lyrics plus chords
- melody dictation with tap-to-edit note controls
- rhythm, tempo, and coaching notes

The current MVP uses a shared username/password instead of full accounts and
stores songs in local SQLite.

## Features

- shared login gate for one teacher/student account
- manual song authoring with structured lyrics, chords, melody, rhythm, and notes
- seeded `Wish You Were Here` lesson card with chord functions and rhythm cues
- in-place melody note editing through native mobile-friendly controls
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
- seed songs now live as JSON files under `seed_data/songs/`
- add a new seed song by creating another `*.json` file in that directory
- Python loads and validates those files at startup, so you do not need a new
  Python file per song

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
