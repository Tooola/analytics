"""Streamlit dashboard — internal admin, monitoring, and testing UI.

Run with: streamlit run dashboard/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Open Analytics AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Make dashboard/ importable so pages/*.py can share the central client too.
_DASHBOARD_DIR = Path(__file__).resolve().parent
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

from api_client import (  # noqa: E402
    cached_health,
    clean_api_url,
    get_api_base,
)

# Resolve the API base once (the Settings expander below can override it).
if not st.session_state.get("api_base"):
    st.session_state["api_base"] = get_api_base()
else:
    st.session_state["api_base"] = clean_api_url(st.session_state["api_base"])
st.session_state.setdefault("api_key", "")


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

# API health indicator (cached 30s — one probe max per 30s, not one per rerun)
health = cached_health(st.session_state.api_base, st.session_state.get("api_key", ""))
if health and health.get("status"):
    status_color = "🟢" if health["status"] == "healthy" else "🟡"
    st.sidebar.markdown(f"{status_color} **{str(health['status']).title()}**")
    st.sidebar.caption(f"API: {st.session_state.api_base}")
    st.sidebar.caption(
        f"DB: {health.get('database', '?')} | Engine: {health.get('ai_provider', '?')}"
    )
else:
    st.sidebar.markdown("🔴 **Offline**")
    st.sidebar.caption(f"API: {st.session_state.api_base}")

st.sidebar.markdown("---")

# Page selection
selection = st.sidebar.radio("Navigate", list(PAGES.keys()))

# API base URL override
with st.sidebar.expander("Settings"):
    new_base = clean_api_url(st.text_input("API Base URL", value=st.session_state.api_base))
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
