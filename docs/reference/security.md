# Security

SingNote is currently a small shared-login app, not a multi-user production
system.

Canonical sources:
- [`src/singnote/config.py`](../../src/singnote/config.py)
- [`src/singnote/auth.py`](../../src/singnote/auth.py)

## Current Security Model

- one shared username/password
- credentials come from environment variables or Streamlit secrets
- local SQLite storage

## Important Limits

- no per-user accounts
- no role separation
- no session store outside Streamlit state
- no hardened secret rotation workflow in the repo

## Safe Practices

- never commit real credentials
- use Streamlit Community Cloud secrets for deployment
- replace any leaked credentials immediately
- treat public repo history as potentially exposed

## Historical Note

The repo previously experimented with other interaction models, but the active
security surface remains the shared-login gate only.
