# SingNote

SingNote is a Streamlit app for shared singing lessons. It presents songs as
practice cards with three coordinated views:

- lyrics + chords
- melody packages
- rhythm notes

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
