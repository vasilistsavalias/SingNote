# Architecture Overview

SingNote is a single-process Streamlit application with local persistence.

Canonical sources:
- [`streamlit_app.py`](../../streamlit_app.py)
- [`src/singnote/bootstrap.py`](../../src/singnote/bootstrap.py)
- [`src/singnote/domain/models.py`](../../src/singnote/domain/models.py)
- [`src/singnote/storage/repository.py`](../../src/singnote/storage/repository.py)

## Runtime Model

- UI runtime: Streamlit
- package code: `src/singnote`
- persistence: SQLite through SQLModel/SQLAlchemy
- structured data validation: Pydantic models
- seed format: YAML-first, legacy JSON still supported

The app boots in-process. There is no service decomposition.

## Boot Sequence

1. `streamlit_app.py` initializes import paths.
2. `bootstrap_application()` loads settings.
3. SQLite schema initialization runs.
4. Seed songs are loaded from disk.
5. Seed-managed records are refreshed if their seed signature changed.
6. The home page renderer displays the login and workspace flow.

## Core Data Model

The canonical domain model is the `Song` object. It contains:

- `lyric_sections`
- `chord_events`
- `melody_notes`
- `rhythm_cues`
- `teacher_annotations`

Each lyric line is a `LyricSegment`. Melody authoring is now package-based at
the segment level through `melody_packages`, where each package owns:

- lyric chunk text
- ordered note list
- package order within the line

`melody_notes` still exists as a flattened compatibility layer derived from the
packages.

## Persistence Strategy

Songs are stored as structured JSON-like payloads inside SQLite rows. The repo
layer distinguishes between:

- seed-managed songs
- user-managed songs

Seed-managed rows update automatically when the seed file changes. Once a song
is edited in the app, it becomes user-managed and later seed refreshes do not
overwrite it automatically.

Recordings are operational user data, not seed data. Their metadata is stored
in SQLite and their audio files are stored under `SINGNOTE_DATA_DIR /
recordings / <song-id>`. Streamlit Community Cloud local storage is not a
durable archive, so important takes should also be kept outside the app.

## UI Shape

The visible app surface is intentionally small:

- login
- song catalog
- selected song workspace

Inside a workspace, the active tabs are:

- `Chords`
- `Melody`
- `Recordings`
- `General`

The active editing model uses native Streamlit controls. The earlier custom
component approach is historical only.
