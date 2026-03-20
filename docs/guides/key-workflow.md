# Song Workflow

This guide explains the main object lifecycle in the current app: a song seed
file becoming a live lesson workspace.

Canonical sources:
- [`seed_data/songs/`](../../seed_data/songs)
- [`src/singnote/seeds.py`](../../src/singnote/seeds.py)
- [`src/singnote/storage/repository.py`](../../src/singnote/storage/repository.py)
- [`src/singnote/ui/home.py`](../../src/singnote/ui/home.py)

## 1. Author Song Data

The preferred authoring format is YAML under `seed_data/songs/`.

A typical line can include:

- `lyrics`
- `chords`
- `melody_text` or `melody_packages`
- `rhythm`

Preferred melody shorthand:

```yaml
melody_text: |
  So = C,B,G
  So = C
  you = B
  think = C
```

This shorthand is converted into structured melody packages during load.

## 2. Load During Bootstrap

At startup, the app reads all `*.yaml`, `*.yml`, and `*.json` seed files from
`seed_data/songs/`.

The loader:

- parses the portable format
- validates notes and structure
- upgrades legacy flat melody arrays when necessary
- returns validated `Song` objects

## 3. Persist Into SQLite

The repository compares the incoming seed signature with the existing row:

- if the row is missing, it inserts it
- if the row is seed-managed and changed on disk, it refreshes it
- if the row was manually edited in the app, it leaves it alone

## 4. Render In The UI

The catalog lists available songs. Selecting a song opens the workspace.

The tabs use the same `Song` object in different projections:

- chords-and-lyrics reader view
- melody reader and melody editing view
- general theory and strumming view

## 5. Refresh Seed Content

If a seed-managed song changes on disk, the repository refreshes it during the
next bootstrap automatically.

If a song has already been edited in the app, the saved database version wins.
To pick up the YAML version again, recreate the local database or remove the
saved row before the next startup.

## Current Contradictions Resolved

- The visible home screen no longer exposes the authoring panel, even though
  helper code for authoring still exists in `src/singnote/ui/authoring.py`.
- The old long-press component files remain in the repo but are not part of
  this workflow.
