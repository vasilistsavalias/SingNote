"""Shared login helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppAccessStatus:
    """Resolved application access state for the current session."""

    requires_login: bool
    is_authenticated: bool

    @property
    def app_access_enabled(self) -> bool:
        """Return whether the current session may use the app."""
        return not self.requires_login or self.is_authenticated


def resolve_app_access(
    configured_username: str | None,
    configured_password: str | None,
    is_authenticated: bool,
) -> AppAccessStatus:
    """Resolve whether the app is available for the current session."""
    requires_login = bool(configured_username and configured_password)
    return AppAccessStatus(
        requires_login=requires_login,
        is_authenticated=is_authenticated if requires_login else True,
    )


def validate_shared_login(
    entered_username: str,
    entered_password: str,
    configured_username: str | None,
    configured_password: str | None,
) -> bool:
    """Validate submitted shared credentials."""
    if not configured_username or not configured_password:
        return True
    return (
        entered_username == configured_username
        and entered_password == configured_password
    )
