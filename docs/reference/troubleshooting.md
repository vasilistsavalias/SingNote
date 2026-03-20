# Troubleshooting

This page covers the main problems that have already appeared in the project.

Canonical sources:
- [`src/singnote/config.py`](../../src/singnote/config.py)
- [`src/singnote/storage/repository.py`](../../src/singnote/storage/repository.py)
- [`src/singnote/seeds.py`](../../src/singnote/seeds.py)

## App Does Not Import `singnote`

Symptom:
- Streamlit Cloud reports `ModuleNotFoundError: No module named 'singnote'`

Cause:
- the app runs from the repo root, while the package lives under `src/`

Current fix:
- [`streamlit_app.py`](../../streamlit_app.py) adds `src/` to `sys.path`

## Updated YAML Does Not Show In The App

Cause:
- the database is still serving the existing saved row

Fix:
1. reboot or redeploy the app if needed
2. if the song is still seed-managed, the new YAML should load on startup
3. if the song was already edited in the app, recreate the local SQLite file or
   remove the saved row so bootstrap can seed it again

## Instrumental Placeholder Rows Keep Showing

Cause:
- instrumental placeholders still exist in the song seed, or the live DB row
  was not reset after seed edits

Fix:
- remove them from the seed file
- then restart with a fresh seed-managed database row

## Melody YAML Fails To Parse

Common causes:

- missing `=` or `=>` in `melody_text`
- invalid note names
- empty package text
- empty note list

Valid example:

```yaml
melody_text: |
  So = C,B,G
  tell = A,D
```

## Streamlit Cloud Still Shows Old UI

Fix:
1. push to `main`
2. open `Manage app`
3. click `Reboot app`

If seed-backed content is still stale after reboot, confirm the live database
is not serving a previously edited song row.
