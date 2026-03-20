# Codebase Tour

This page gives a fast orientation of the active codebase.

Canonical sources:
- [`streamlit_app.py`](../../streamlit_app.py)
- [`src/singnote/bootstrap.py`](../../src/singnote/bootstrap.py)
- [`src/singnote/ui/home.py`](../../src/singnote/ui/home.py)
- [`src/singnote/seeds.py`](../../src/singnote/seeds.py)
- [`src/singnote/storage/repository.py`](../../src/singnote/storage/repository.py)

## Entry Path

1. [`streamlit_app.py`](../../streamlit_app.py) adds `src/` to `sys.path`
   and calls `main()`.
2. `main()` imports `bootstrap_application()`.
3. [`bootstrap.py`](../../src/singnote/bootstrap.py) loads settings, creates
   the SQLite engine, loads seed songs, and returns the application context.
4. `Application.render()` calls the home page renderer in
   [`home.py`](../../src/singnote/ui/home.py).

## Main Modules

- [`src/singnote/config.py`](../../src/singnote/config.py)
  Reads environment variables and Streamlit secrets.
- [`src/singnote/domain/models.py`](../../src/singnote/domain/models.py)
  Defines the validated song model, including lyric sections, melody packages,
  chord events, rhythm cues, and teacher annotations.
- [`src/singnote/seeds.py`](../../src/singnote/seeds.py)
  Loads portable YAML or legacy JSON songs from `seed_data/songs/`.
- [`src/singnote/storage/repository.py`](../../src/singnote/storage/repository.py)
  Persists songs to SQLite and manages seed refresh behavior.
- [`src/singnote/ui/home.py`](../../src/singnote/ui/home.py)
  Renders the login screen, catalog, workspace, sidebar tools, and tab UIs.
- [`src/singnote/ui/authoring.py`](../../src/singnote/ui/authoring.py)
  Contains authoring and serialization helpers. The current main screen hides
  the authoring panel, but the code still exists.
- [`src/singnote/ui/theme.py`](../../src/singnote/ui/theme.py)
  Injects the active Streamlit visual styling.

## Data Locations

- seed songs:
  [`seed_data/songs/`](../../seed_data/songs)
- local runtime database:
  [`instance/`](../../instance)
- tests:
  [`tests/`](../../tests)

## Important Runtime Truths

- There is no separate backend API.
- There is no worker queue.
- SQLite is the only persistence layer in this repository.
- Seed songs are source data, but manually edited seeded songs become
  user-managed in the database until explicitly reset from seed.

## Historical Residue

The repository still contains files under
[`src/singnote/components/`](../../src/singnote/components) for an earlier
custom long-press editor concept. Those files are not part of the active UI
path today.
