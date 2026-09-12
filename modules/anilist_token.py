"""
# AniList Token Module

Host AniList OAuth token storage and lifecycle helpers (PIN flow).

Access/refresh tokens live in ``database/anilist_token.json`` (mode 0600,
gitignored, covered by encrypted backups) instead of ``.env``. Only the
client details (ID, secret, redirect URI) remain environment configuration.

On first load, tokens are migrated once from legacy ``.env`` variables
(``ANILIST_ACCESS_TOKEN`` plus either ``ANILIST_OAUTH_*`` or the documented
``ANILIST_REFRESH_TOKEN``/``ANILIST_TOKEN_EXPIRY`` names, which were never
actually read due to the name mismatch).
"""

import json
import os
import time
import urllib.parse
from dataclasses import asdict, dataclass
from typing import Any

import aiohttp

from classes.excepts import ProviderHttpError
from modules.const import (
    ANILIST_CLIENT_ID,
    ANILIST_CLIENT_SECRET,
    ANILIST_REDIRECT_URI,
)
from modules.filecache import cached_file, drop_cached_file

TOKEN_PATH = "database/anilist_token.json"
"""Location of the host AniList token file (gitignored, 0600)"""

REFRESH_THRESHOLD = 7 * 86400
"""Refresh proactively when fewer than this many seconds remain (7 days)"""

REFRESH_RETRY_COOLDOWN = 600
"""Wait this long after a failed refresh before retrying (10 minutes)"""

_last_refresh_failure: float = 0
"""Timestamp of the last failed refresh attempt (backoff guard)"""


@dataclass
class AniListToken:
    """Host AniList OAuth token"""

    access_token: str
    """Bearer token for GraphQL requests"""
    refresh_token: str
    """Token used to obtain a new access token"""
    expires_at: float | None
    """Absolute expiry as Unix timestamp, None when unknown"""
    updated_at: float
    """Unix timestamp of when this token was obtained"""

    def expires_in(self) -> float | None:
        """
        Seconds until expiry.

        Returns:
            float | None: Seconds remaining, negative when expired, None when unknown
        """
        if self.expires_at is None:
            return None
        return self.expires_at - time.time()


def get_authorize_url() -> str:
    """
    Build the AniList PIN authorization URL for the host to visit.

    Returns:
        str: The browser URL to authorize the bot and obtain a PIN
    """
    params = urllib.parse.urlencode(
        {
            "client_id": ANILIST_CLIENT_ID,
            "redirect_uri": ANILIST_REDIRECT_URI,
            "response_type": "code",
        }
    )
    return f"https://anilist.co/api/v2/oauth/authorize?{params}"


async def _request_token(payload: dict[str, Any]) -> dict[str, Any]:
    """
    POST an OAuth grant to AniList and return the raw token payload.

    Args:
        payload (dict[str, Any]): The grant parameters

    Raises:
        ProviderHttpError: When AniList rejects the grant or no token is returned

    Returns:
        dict[str, Any]: The raw token response
    """
    headers = {"Accept": "application/json"}
    async with (
        aiohttp.ClientSession() as session,
        session.post(
            "https://anilist.co/api/v2/oauth/token",
            json=payload,
            headers=headers,
        ) as response,
    ):
        try:
            data: dict[str, Any] = await response.json()
        except Exception as err:
            raise ProviderHttpError(str(err), response.status) from err
    if response.status != 200 or not data.get("access_token"):
        detail = data.get("message", data)
        raise ProviderHttpError(str(detail), response.status)
    return data


def _from_response(data: dict[str, Any]) -> AniListToken:
    """
    Normalize a raw AniList token response into an AniListToken.

    Args:
        data (dict[str, Any]): The raw token response

    Returns:
        AniListToken: The normalized token
    """
    now = time.time()
    try:
        lifetime = float(data.get("expires_in", 0) or 0)
    except (TypeError, ValueError):
        lifetime = 0
    return AniListToken(
        access_token=str(data["access_token"]),
        refresh_token=str(data.get("refresh_token", "")),
        expires_at=(now + lifetime) if lifetime > 0 else None,
        updated_at=now,
    )


async def exchange_pin(pin: str) -> AniListToken:
    """
    Exchange an AniList PIN (authorization code) for tokens.

    Args:
        pin (str): The PIN shown by AniList after authorizing

    Raises:
        ProviderHttpError: When AniList rejects the PIN

    Returns:
        AniListToken: The obtained token (not yet saved)
    """
    return _from_response(
        await _request_token(
            {
                "grant_type": "authorization_code",
                "client_id": ANILIST_CLIENT_ID,
                "client_secret": ANILIST_CLIENT_SECRET,
                "redirect_uri": ANILIST_REDIRECT_URI,
                "code": pin.strip(),
            }
        )
    )


async def refresh_token(token: AniListToken) -> AniListToken:
    """
    Refresh an access token using its refresh token.

    Args:
        token (AniListToken): The token holding the refresh token

    Raises:
        ProviderHttpError: When AniList rejects the refresh grant

    Returns:
        AniListToken: The new token (not yet saved)
    """
    return _from_response(
        await _request_token(
            {
                "grant_type": "refresh_token",
                "client_id": ANILIST_CLIENT_ID,
                "client_secret": ANILIST_CLIENT_SECRET,
                "redirect_uri": ANILIST_REDIRECT_URI,
                "refresh_token": token.refresh_token,
            }
        )
    )


def _parse_expiry(value: str | None) -> float | None:
    """
    Parse a legacy expiry env value into an absolute timestamp.

    Args:
        value (str | None): The raw env value

    Returns:
        float | None: Absolute Unix timestamp or None when unparsable
    """
    if not value:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    if number < 1e12:
        return number
    return number / 1000


def _migrate_from_env() -> AniListToken | None:
    """
    One-time migration of legacy ``.env`` tokens into an AniListToken.

    Returns:
        AniListToken | None: The migrated token or None when absent
    """
    access = os.getenv("ANILIST_ACCESS_TOKEN")
    if not access:
        return None
    refresh = os.getenv("ANILIST_OAUTH_REFRESH") or os.getenv("ANILIST_REFRESH_TOKEN")
    expiry = _parse_expiry(os.getenv("ANILIST_OAUTH_EXPIRY")) or _parse_expiry(
        os.getenv("ANILIST_TOKEN_EXPIRY")
    )
    return AniListToken(
        access_token=access,
        refresh_token=refresh or "",
        expires_at=expiry,
        updated_at=time.time(),
    )


def _read_token_file(path: str = TOKEN_PATH) -> AniListToken | None:
    """
    Read the token file, migrating legacy ``.env`` tokens on first run.

    Args:
        path (str, optional): Token file path. Defaults to TOKEN_PATH.

    Returns:
        AniListToken | None: The stored token or None when logged out
    """
    if os.path.exists(path):
        with open(path, encoding="utf-8") as file:
            data: dict[str, Any] = json.load(file)
        return AniListToken(
            access_token=str(data["access_token"]),
            refresh_token=str(data.get("refresh_token", "")),
            expires_at=data.get("expires_at"),
            updated_at=float(data.get("updated_at", time.time())),
        )
    migrated = _migrate_from_env()
    if migrated is not None:
        save_token(migrated, path)
    return migrated


def load_token(path: str = TOKEN_PATH) -> AniListToken | None:
    """
    Load the stored host token (memoized per file version).

    Args:
        path (str, optional): Token file path. Defaults to TOKEN_PATH.

    Returns:
        AniListToken | None: The stored token or None when logged out
    """
    return cached_file(path, lambda: _read_token_file(path))


def save_token(token: AniListToken, path: str = TOKEN_PATH) -> None:
    """
    Persist the host token with owner-only permissions.

    Args:
        token (AniListToken): The token to store
        path (str, optional): Token file path. Defaults to TOKEN_PATH.

    Returns:
        None
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    with os.fdopen(os.open(path, flags, 0o600), "w", encoding="utf-8") as file:
        json.dump(asdict(token), file, indent=2)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    drop_cached_file(path)


def clear_token(path: str = TOKEN_PATH) -> bool:
    """
    Delete the stored host token (logout).

    Args:
        path (str, optional): Token file path. Defaults to TOKEN_PATH.

    Returns:
        bool: True when a token was deleted, False when already logged out
    """
    drop_cached_file(path)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def token_needs_refresh(
    token: AniListToken, threshold: float = REFRESH_THRESHOLD
) -> bool:
    """
    Decide whether a token should be refreshed.

    Args:
        token (AniListToken): The token to inspect
        threshold (float, optional): Refresh below this many remaining seconds.
            Defaults to REFRESH_THRESHOLD.

    Returns:
        bool: True when expired, expiring soon, or expiry unknown
    """
    if not token.refresh_token:
        return False
    remaining = token.expires_in()
    if remaining is None:
        return True
    return remaining < threshold


async def get_valid_access_token(path: str = TOKEN_PATH) -> str | None:
    """
    Return a usable host access token, refreshing transparently when needed.

    A failed refresh backs off briefly; the previous token is kept when it
    has not expired yet.

    Args:
        path (str, optional): Token file path. Defaults to TOKEN_PATH.

    Returns:
        str | None: The access token or None when logged out
    """
    global _last_refresh_failure
    token = load_token(path)
    if token is None:
        return None
    if token_needs_refresh(token):
        if time.time() - _last_refresh_failure < REFRESH_RETRY_COOLDOWN:
            return token.access_token
        try:
            token = await refresh_token(token)
        except ProviderHttpError:
            _last_refresh_failure = time.time()
            return token.access_token
        save_token(token, path)
    return token.access_token


async def ensure_fresh_token(
    threshold: float = REFRESH_THRESHOLD,
    path: str = TOKEN_PATH,
) -> tuple[bool, str]:
    """
    Proactively refresh the stored token when it needs it (task entrypoint).

    Args:
        threshold (float, optional): Refresh below this many remaining seconds.
            Defaults to REFRESH_THRESHOLD.
        path (str, optional): Token file path. Defaults to TOKEN_PATH.

    Raises:
        ProviderHttpError: When the refresh grant is rejected

    Returns:
        tuple[bool, str]: (refreshed, human-readable status message)
    """
    token = load_token(path)
    if token is None:
        return False, "No AniList token stored, skipping refresh"
    if not token_needs_refresh(token, threshold):
        remaining = token.expires_in()
        if remaining is None:
            return False, "AniList token has no refresh token configured"
        days = remaining / 86400
        return False, f"AniList token still valid for {days:.1f} day(s)"
    fresh = await refresh_token(token)
    save_token(fresh, path)
    return True, "AniList token refreshed successfully"


__all__ = [
    "REFRESH_RETRY_COOLDOWN",
    "REFRESH_THRESHOLD",
    "TOKEN_PATH",
    "AniListToken",
    "clear_token",
    "ensure_fresh_token",
    "exchange_pin",
    "get_authorize_url",
    "get_valid_access_token",
    "load_token",
    "refresh_token",
    "save_token",
    "token_needs_refresh",
]
