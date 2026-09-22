"""Security utilities — API key generation, hashing, and verification.

API keys are never stored in plain text. We store only a SHA-256 hash of the
key so that a database compromise does not expose usable keys. The raw key is
shown to the user exactly once at creation time.
"""

from __future__ import annotations

import hashlib
import secrets
import string

from passlib.context import CryptContext

from app.core.config import settings

# passlib is used for any future password hashing needs (e.g. dashboard login).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
