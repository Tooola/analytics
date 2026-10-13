"""Security utilities — API key generation, hashing, and verification.

API keys are never stored in plain text. We store only a SHA-256 hash of
the key so that a database compromise does not expose usable keys. The raw
key is shown to the user exactly once at creation time.

Dashboard operator accounts (React login) use bcrypt password hashes and
short-lived JWT bearer tokens — see the bottom of this module.
"""

from __future__ import annotations

import hashlib
import secrets
import string
from datetime import datetime, timezone

import bcrypt
import jwt

from app.core.config import settings

# Character set for generated API keys — alphanumeric, unambiguous.
_KEY_ALPHABET = string.ascii_letters + string.digits


def generate_api_key() -> str:
    """Generate a new random API key (40 URL-safe characters)."""
    prefix = settings.api_key_prefix
    if prefix and not prefix.endswith("_"):
        prefix += "_"
    return prefix + "".join(secrets.choice(_KEY_ALPHABET) for _ in range(40))


def hash_api_key(raw_key: str) -> str:
    """Return a deterministic SHA-256 hash of *raw_key*.

    SHA-256 is appropriate here because API keys are high-entropy random
    strings, so rainbow tables are not a concern. We mix in a deployment
    secret to prevent hash comparison across environments.
    """
    payload = f"{settings.api_key_hash_secret}:{raw_key}"
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Constant-time comparison of a raw key against a stored hash."""
    candidate = hash_api_key(raw_key)
    return secrets.compare_digest(candidate, stored_hash)


# ─── Dashboard login (operator accounts) ────────────────────────────────────
# bcrypt is used directly: passlib 1.7.4 (its last release) is broken with
# bcrypt >= 4.1 and unmaintained.


def hash_password(raw_password: str) -> str:
    """Hash a dashboard password with bcrypt (salted, adaptive cost).

    bcrypt only considers the first 72 bytes of a password — plenty for
    operator credentials (secrets.token_urlsafe-style).
    """
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()


def verify_password(raw_password: str, password_hash: str) -> bool:
    """Check a raw password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(raw_password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False


def create_dashboard_token(user_id: str, username: str) -> tuple[str, int]:
    """Create a signed dashboard JWT (HS256). Returns (token, ttl_seconds).

    Signed with the deployment secret (same one as API key hashing): no
    extra env var to manage — and production already refuses to boot
    without it.
    """
    now = datetime.now(timezone.utc)
    ttl_seconds = settings.dashboard_token_expire_minutes * 60
    payload = {
        "sub": user_id,
        "username": username,
        "type": "dashboard",
        "iat": int(now.timestamp()),
        "exp": int(now.timestamp()) + ttl_seconds,
    }
    token = jwt.encode(payload, settings.api_key_hash_secret, algorithm="HS256")
    return token, ttl_seconds


def decode_dashboard_token(token: str) -> dict:
    """Decode and validate a dashboard JWT.

    Raises ``jwt.PyJWTError`` (incl. expiry) on any problem — callers
    translate that into a 401.
    """
    return jwt.decode(token, settings.api_key_hash_secret, algorithms=["HS256"])
