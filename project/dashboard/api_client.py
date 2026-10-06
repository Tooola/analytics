"""Central API client for the Streamlit dashboard (PLAN.md V4/V6).

One place for everything the 7 previous copies used to do 6-7 times each:
- API base URL resolution (session override → st.secrets → env → Railway default)
- X-API-Key injection from session state
- timeouts (per-call override: /analyze uses 60s, endpoint probes 5s)
- transport errors: `requests.RequestException` — NOT `ConnectionError`,
  because a `ReadTimeout` is not a ConnectionError and used to crash pages
- safe JSON parsing (`json_or`): a non-JSON body never takes a page down
"""

from __future__ import annotations

import os

import requests
import streamlit as st

FALLBACK_API_BASE = "https://scintillating-kindness-production-d038.up.railway.app"


def clean_api_url(url) -> str:
    """Normalise an API base URL (tolerates empty values and .env-style prefixes)."""
    if not url:
        return ""
    url = str(url).strip()
    if url.startswith("API_BASE_URL="):  # tolerate raw .env lines pasted in Settings
        url = url[len("API_BASE_URL="):].strip()
    return url.rstrip("/")


def get_api_base() -> str:
    """Resolve the API base: session override → secrets → env → fallback."""
    session_base = st.session_state.get("api_base")
    if session_base:
        return clean_api_url(session_base)
    try:
        if hasattr(st, "secrets"):
            if "api_base_url" in st.secrets:
                return clean_api_url(st.secrets["api_base_url"])
            if "API_BASE_URL" in st.secrets:
                return clean_api_url(st.secrets["API_BASE_URL"])
    except Exception:
        pass  # no secrets file (local/default deployments)
    return clean_api_url(os.environ.get("API_BASE_URL", FALLBACK_API_BASE))


def build_headers(extra: dict | None = None) -> dict:
    """Session API key + per-call overrides (extra wins on key conflicts)."""
    headers: dict = {}
    key = st.session_state.get("api_key", "")
    if key:
        headers["X-API-Key"] = key
    if extra:
        headers.update(extra)
    return headers


def get(path: str, headers: dict | None = None, timeout: float = 10, **kwargs):
    try:
        return requests.get(
            f"{get_api_base()}{path}",
            headers=build_headers(headers),
            timeout=timeout,
            **kwargs,
        )
    except requests.RequestException:
        return None


def post(
    path: str,
    json_data=None,
    headers: dict | None = None,
    timeout: float = 10,
    **kwargs,
):
    try:
        return requests.post(
            f"{get_api_base()}{path}",
            json=json_data,
            headers=build_headers(headers),
            timeout=timeout,
            **kwargs,
        )
    except requests.RequestException:
        return None


def delete(path: str, headers: dict | None = None, timeout: float = 10, **kwargs):
    try:
        return requests.delete(
            f"{get_api_base()}{path}",
            headers=build_headers(headers),
            timeout=timeout,
            **kwargs,
        )
    except requests.RequestException:
        return None


def json_or(response, default=None):
    """Parse a successful response as JSON; never raises.

    Covers: no response (network error), non-200, and 200-with-HTML-body
    (reverse proxies love serving HTML error pages with 200).
    """
    if response is None or response.status_code != 200:
        return default
    try:
        data = response.json()
    except ValueError:
        return default
    return default if data is None else data


# ─── Cached probes (V5) ──────────────────────────────────────────────────────
# st.cache_data functions cannot read session_state reliably → base/key are
# explicit arguments, which also makes them part of the cache key.


@st.cache_data(ttl=30, show_spinner=False)
def cached_health(base: str, api_key: str) -> dict | None:
    """GET /health, cached 30s. Shared by the sidebar and the overview page."""
    try:
        resp = requests.get(
            f"{base}/api/v1/health",
            headers={"X-API-Key": api_key} if api_key else {},
            timeout=5,
        )
    except requests.RequestException:
        return None
    data = json_or(resp)
    return data if isinstance(data, dict) else None


@st.cache_data(ttl=60, show_spinner=False)
def cached_get(base: str, api_key: str, path: str, timeout: float = 10):
    """GET → parsed JSON (or None), cached 60s. Used by list/count views."""
    try:
        resp = requests.get(
            f"{base}{path}",
            headers={"X-API-Key": api_key} if api_key else {},
            timeout=timeout,
        )
    except requests.RequestException:
        return None
    return json_or(resp)


@st.cache_data(ttl=60, show_spinner=False)
def cached_probe_endpoints(
    base: str, api_key: str, endpoints: tuple
) -> tuple[tuple[str, str, str], ...]:
    """Probe the status of each endpoint (GET only), cached 60s."""
    headers = {"X-API-Key": api_key} if api_key else {}
    out = []
    for method, path, _desc in endpoints:
        if method != "GET":
            out.append((method, path, "N/A (POST)"))
            continue
        try:
            resp = requests.get(f"{base}{path}", headers=headers, timeout=5)
            status = str(resp.status_code)
        except requests.RequestException:
            status = "UNREACHABLE"
        out.append((method, path, status))
    return tuple(out)
