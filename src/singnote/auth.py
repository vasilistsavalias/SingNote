"""Shared login and persistent session cookie helpers."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

AUTH_COOKIE_NAME = "singnote_auth"
AUTH_COOKIE_MAX_AGE_SECONDS = 365 * 24 * 60 * 60  # 1 year


@dataclass(frozen=True)
class AppAccessStatus:
    """Resolved application access state for the current session."""

    requires_login: bool
    is_authenticated: bool

    @property
    def app_access_enabled(self) -> bool:
        """Return whether the current session may use the app."""
        return not self.requires_login or self.is_authenticated


def generate_session_token(
    configured_username: str | None,
    configured_password: str | None,
) -> str:
    """Derive a stable, tamper-proof session token for configured credentials."""
    if not configured_username or not configured_password:
        return ""
    seed = (
        f"singnote:{configured_username}:{configured_password}".encode(
            "utf-8"
        )
    )
    return hmac.new(
        b"singnote-persistent-auth-v1",
        seed,
        hashlib.sha256,
    ).hexdigest()


def validate_session_token(
    token: str | None,
    configured_username: str | None,
    configured_password: str | None,
) -> bool:
    """Validate whether a cookie session token matches active configured credentials."""
    if not configured_username or not configured_password:
        return True
    if not token or not isinstance(token, str):
        return False
    expected = generate_session_token(configured_username, configured_password)
    return hmac.compare_digest(token.strip(), expected)


def resolve_app_access(
    configured_username: str | None,
    configured_password: str | None,
    is_authenticated: bool,
    cookie_token: str | None = None,
) -> AppAccessStatus:
    """Resolve whether the app is available for the current session."""
    requires_login = bool(configured_username and configured_password)
    if not requires_login:
        return AppAccessStatus(requires_login=False, is_authenticated=True)

    has_valid_cookie = validate_session_token(
        cookie_token,
        configured_username,
        configured_password,
    )
    return AppAccessStatus(
        requires_login=True,
        is_authenticated=bool(is_authenticated or has_valid_cookie),
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

