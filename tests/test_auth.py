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
