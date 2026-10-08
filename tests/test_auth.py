"""Tests for shared app login access."""

from __future__ import annotations

from singnote.auth import resolve_app_access, validate_shared_login


def test_app_is_public_when_shared_login_is_not_configured() -> None:
    """The app remains open in development with no shared login configured."""
    access = resolve_app_access(None, None, is_authenticated=False)

    assert access.requires_login is False
    assert access.app_access_enabled is True


def test_app_requires_authentication_when_shared_login_exists() -> None:
    """Configured shared credentials should gate the app."""
    access = resolve_app_access("teacher", "teacher-pass", False)

    assert access.requires_login is True
    assert access.app_access_enabled is False


def test_validate_shared_login_checks_username_and_password() -> None:
    """Only the configured shared credentials should unlock the app."""
    assert (
        validate_shared_login(
            "teacher",
            "teacher-pass",
            "teacher",
            "teacher-pass",
        )
        is True
    )
    assert (
        validate_shared_login(
            "teacher",
            "wrong",
            "teacher",
            "teacher-pass",
        )
        is False
    )


def test_session_token_generation_and_validation() -> None:
    """Session tokens should be deterministic and validate correctly."""
    from singnote.auth import (
        generate_session_token,
        validate_session_token,
    )

    token = generate_session_token("teacher", "secret123")
    assert isinstance(token, str) and len(token) == 64

    # Valid token matches
    assert validate_session_token(token, "teacher", "secret123") is True

    # Bad token or mismatched credentials fail
    assert validate_session_token("badtoken", "teacher", "secret123") is False
    assert validate_session_token(token, "student", "secret123") is False
    assert validate_session_token(None, "teacher", "secret123") is False


def test_app_access_auto_authenticated_with_valid_cookie() -> None:
    """A valid cookie session token should grant access without manual login."""
    from singnote.auth import generate_session_token

    token = generate_session_token("teacher", "secret123")
    access = resolve_app_access(
        "teacher",
        "secret123",
        is_authenticated=False,
        cookie_token=token,
    )

    assert access.requires_login is True
    assert access.is_authenticated is True
    assert access.app_access_enabled is True


def test_app_access_denied_with_invalid_cookie() -> None:
    """An invalid cookie session token should keep the login gate active."""
    access = resolve_app_access(
        "teacher",
        "secret123",
        is_authenticated=False,
        cookie_token="tampered-or-expired",
    )

    assert access.requires_login is True
    assert access.is_authenticated is False
    assert access.app_access_enabled is False

