"""Streamlit dashboard — internal admin, monitoring, and testing UI.

Run with: streamlit run dashboard/app.py
"""

from __future__ import annotations

import hmac
import os
import sys
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Open Analytics AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Make dashboard/ importable so views/*.py can share the central client too.
_DASHBOARD_DIR = Path(__file__).resolve().parent
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

from api_client import (  # noqa: E402
    cached_health,
    clean_api_url,
    get_api_base,
)

# ─── Optional dashboard access gate (PLAN.md V3) ────────────────────────────
# Disabled unless DASHBOARD_PASSWORD (env) or secrets.dashboard_password is
# set — existing deployments keep behaving exactly as before.


def _dashboard_password() -> str:
    try:
        if hasattr(st, "secrets") and "dashboard_password" in st.secrets:
            return str(st.secrets["dashboard_password"])
    except Exception:
        pass  # no secrets file (local/default deployments)
    return os.environ.get("DASHBOARD_PASSWORD", "")


_password = _dashboard_password()
if _password and not st.session_state.get("dashboard_unlocked"):
    st.title("🔐 Open Analytics AI")
    st.caption("This dashboard is protected — enter the access password.")
    with st.form("dashboard_login"):
        entered = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter")
    if submitted and entered:
        if hmac.compare_digest(entered.encode(), _password.encode()):
            st.session_state["dashboard_unlocked"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


# Resolve the API base once (the Settings expander below can override it).
if not st.session_state.get("api_base"):
    st.session_state["api_base"] = get_api_base()
else:
    st.session_state["api_base"] = clean_api_url(st.session_state["api_base"])
st.session_state.setdefault("api_key", "")


# ─── Sidebar navigation ────────────────────────────────

PAGES = {
    "Overview": "views/overview.py",
    "Applications": "views/applications.py",
    "Datasets": "views/datasets.py",
    "Analytics": "views/analytics.py",
    "Playground": "views/ai_playground.py",
    "System": "views/system.py",
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
page_file_path = base_dir / "views" / page_filename

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
