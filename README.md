# SingNote

SingNote is a mobile-first Streamlit app for teacher-student singing practice.
It keeps songs as reusable lesson cards with three coordinated tabs:

- lyrics plus chords
- melody dictation with long-press note editing
- rhythm, tempo, and coaching notes

The current MVP uses a shared username/password instead of full accounts and
stores songs in local SQLite.

## Features

- shared login gate for one teacher/student account
- manual song authoring with structured lyrics, chords, melody, rhythm, and notes
- seeded `Wish You Were Here` lesson card with chord functions and rhythm cues
- in-place melody note editing through a custom long-press component
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
- seeded phrase labels are intentionally short cues, so teachers can replace them
  with licensed full lyrics inside the authoring panel

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
