"""Rate limiting — shared slowapi Limiter instance.

Lives in its own module because BOTH ``app.main`` (to attach it to the app)
and the route modules (to decorate expensive endpoints) need the instance;
importing it from ``app.main`` would create a circular import.

Design notes:
- Limits are declared per-route (heavy/expensive POSTs only). A global
  ``default_limits`` + middleware would throttle the Streamlit dashboard,
  which fires several GETs on every rerun.
- Bucket strategy: API key when the request carries one (each tenant gets
  its own quota even if every client sits behind the same proxy IP),
  else first X-Forwarded-For hop, else socket address.
"""

from __future__ import annotations

import hashlib

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def client_bucket(request: Request) -> str:
    """Identify the caller for rate-limit accounting (never logs the raw key)."""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        digest = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return f"key:{digest}"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=client_bucket,
    # Matches the historical flag: only the literal env "test" disables it
    # (tests run as APP_ENV=testing and DO exercise the limiter).
    enabled=settings.app_env != "test",
)
