"""Streamlit dashboard — internal admin, monitoring, and testing UI.

Run with: streamlit run dashboard/app.py
"""

from __future__ import annotations

import requests
import streamlit as st

st.set_page_config(
    page_title="Open Analytics AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os
from pathlib import Path

DEFAULT_API_BASE = "https://scintillating-kindness-production-d038.up.railway.app"
API_BASE = os.environ.get("API_BASE_URL", DEFAULT_API_BASE)

try:
    if hasattr(st, "secrets"):
        if "api_base_url" in st.secrets:
            API_BASE = st.secrets["api_base_url"]
        elif "API_BASE_URL" in st.secrets:
            API_BASE = st.secrets["API_BASE_URL"]
except Exception:
    pass

# Try loading from env file if running locally
try:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, _, val = line.partition("=")
                if key.strip() == "API_BASE_URL":
                    API_BASE = val.strip()
except Exception:
    pass

# Always overwrite session state so stale cached values (e.g. localhost:8000) are never used
st.session_state["api_base"] = API_BASE
st.session_state.setdefault("api_key", "")


def _build_headers(headers=None):
    req_headers = {}
    if st.session_state.get("api_key"):
        req_headers["X-API-Key"] = st.session_state.api_key
    if headers:
        req_headers.update(headers)
    return req_headers


def api_get(path: str, headers=None, **kwargs):
    try:
        r = requests.get(
            f"{st.session_state.api_base}{path}",
            headers=_build_headers(headers),
            timeout=10,
            **kwargs,
        )
        return r
    except requests.ConnectionError:
        st.error(f"Cannot reach API at {st.session_state.api_base}. Is the backend running?")
        return None


def api_post(path: str, json_data=None, headers=None):
    try:
        r = requests.post(
            f"{st.session_state.api_base}{path}",
            json=json_data,
            headers=_build_headers(headers),
            timeout=30,
        )
        return r
    except requests.ConnectionError:
        st.error(f"Cannot reach API at {st.session_state.api_base}. Is the backend running?")
        return None


def api_delete(path: str, headers=None):
    try:
        r = requests.delete(
            f"{st.session_state.api_base}{path}",
            headers=_build_headers(headers),
            timeout=10,
        )
        return r
    except requests.ConnectionError:
        st.error(f"Cannot reach API at {st.session_state.api_base}. Is the backend running?")
        return None


# ─── Sidebar navigation ────────────────────────────────

PAGES = {
    "Overview": "pages/overview.py",
    "Applications": "pages/applications.py",
    "Datasets": "pages/datasets.py",
    "Analytics": "pages/analytics.py",
    "Playground": "pages/ai_playground.py",
    "System": "pages/system.py",
}

st.sidebar.title("Open Analytics")
st.sidebar.markdown("---")

# API health indicator
health_resp = api_get("/api/v1/health")
if health_resp and health_resp.status_code == 200:
    health = health_resp.json()
    status_color = "🟢" if health["status"] == "healthy" else "🟡"
    st.sidebar.markdown(f"{status_color} **{health['status'].title()}**")
    st.sidebar.caption(f"API: {st.session_state.api_base}")
    st.sidebar.caption(f"DB: {health['database']} | Engine: {health['ai_provider']}")
else:
    st.sidebar.markdown("🔴 **Offline**")
    st.sidebar.caption(f"API: {st.session_state.api_base}")

st.sidebar.markdown("---")

# Page selection
selection = st.sidebar.radio("Navigate", list(PAGES.keys()))

# API base URL override
with st.sidebar.expander("Settings"):
    new_base = st.text_input("API Base URL", value=st.session_state.api_base)
    if new_base != st.session_state.api_base:
        st.session_state.api_base = new_base
        st.rerun()
    new_key = st.text_input("API Key (X-API-Key)", value=st.session_state.get("api_key", ""), type="password", placeholder="anal_...")
    if new_key != st.session_state.get("api_key", ""):
        st.session_state.api_key = new_key
        st.rerun()

# Route to the selected page
page_filename = PAGES[selection].split('/')[-1]
base_dir = Path(__file__).parent
page_file_path = base_dir / "pages" / page_filename

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("page", str(page_file_path))
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        st.warning(f"Page '{selection}' is not yet available.")
except FileNotFoundError:
    st.warning(f"Page '{selection}' is not yet available.")
except Exception as e:
    st.error(f"Error loading page: {e}")
