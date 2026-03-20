# SingNote

SingNote is a Streamlit app for shared singing lessons. It presents songs as
practice cards with three coordinated views:

- chords with lyrics
- melody reader and melody editing
- general song guidance

The active runtime is a single Streamlit app backed by SQLite and YAML seed
files. There is no separate API server, background worker, or cloud service in
this repository.

## Quickstart

```powershell
pip install -e .[dev]
$env:SINGNOTE_SHARED_USERNAME = "shared-teacher"
$env:SINGNOTE_SHARED_PASSWORD = "change-me-before-deploy"
python -m streamlit run streamlit_app.py
```

## Docs

Start with [docs/index.md](docs/index.md).

Key pages:

- [Quickstart](docs/getting-started/quickstart.md)
- [Codebase Tour](docs/getting-started/codebase-tour.md)
- [Architecture Overview](docs/guides/architecture-overview.md)
- [Song Authoring Workflow](docs/guides/key-workflow.md)
- [Commands Reference](docs/reference/commands.md)
- [Troubleshooting](docs/reference/troubleshooting.md)

## Current UX

- login with one shared teacher/student account
- open a song from the catalog
- use `Chords` for lyric-following with auto-scroll
- use `Melody` in `Reader` or `Edit` mode
- use `General` for key, time, tempo, chord quality, and strumming guidance

Seed songs are authored as YAML under [`seed_data/songs/`](seed_data/songs).
The normal workflow is to edit those files directly rather than author songs in
the live UI.

## Repo Map

- [`streamlit_app.py`](streamlit_app.py): Streamlit entrypoint
- [`src/singnote/`](src/singnote): app code
- [`seed_data/songs/`](seed_data/songs): YAML/JSON seed songs
- [`tests/`](tests): pytest suite
- [`instance/`](instance): local SQLite database by default
- [`docs/`](docs): human-facing documentation

## Runtime Artifacts

- local database: `instance/singnote.db` unless `SINGNOTE_DATA_DIR` overrides it
- seed songs: `seed_data/songs/*.yaml` and legacy `*.json`
- Streamlit config: `.streamlit/config.toml`

## Active vs Historical

The active UI uses native Streamlit controls. Older custom long-press component
files still exist in the repository, but they are not part of the active app
path.

## License

This repository is licensed under `AGPL-3.0-only`. If someone modifies the
code and runs it as a networked app, they must keep that derivative open under
the same license.
