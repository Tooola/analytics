"""System page — API status, database status, AI provider, and logs."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# dashboard/ on sys.path → share the central API client (PLAN.md V4)
_DASHBOARD_DIR = Path(__file__).resolve().parent.parent
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

from api_client import (  # noqa: E402
    cached_health,
    cached_probe_endpoints,
    get,
    get_api_base,
)

st.title("System")
st.markdown("Monitor API health, database connectivity, AI provider status, and recent activity.")

base = get_api_base()
key = st.session_state.get("api_key", "")

# ─── API Health ─────────────────────────────────────────

st.subheader("API Status")

h = cached_health(base, key)
if h and h.get("status"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        status_icon = "🟢" if h["status"] == "healthy" else "🟡"
        st.metric("Status", f"{status_icon} {str(h['status']).title()}")
    with c2:
        db_val = str(h.get("database", "?"))
        db_icon = "🟢" if db_val == "connected" else "🔴"
        st.metric("Database", f"{db_icon} {db_val.title()}")
    with c3:
        st.metric("AI Provider", str(h.get("ai_provider", "?")))
    with c4:
        st.metric("Version", str(h.get("version", "?")))

    st.caption(f"Last checked: {h.get('timestamp', 'N/A')}")
else:
    st.error("API is not reachable. Check that the backend is running.")

st.markdown("---")

# ─── API Endpoints ──────────────────────────────────────

st.subheader("API Endpoints")

endpoints = [
    # GET /api/v1/health is not listed: its status is the "API Status"
    # section above (probed from the same shared 30s cache).
    ("GET", "/api/v1/applications", "List applications"),
    ("POST", "/api/v1/applications", "Register application"),
    ("GET", "/api/v1/datasets", "List datasets"),
    ("POST", "/api/v1/datasets", "Register dataset"),
    ("POST", "/api/v1/analyze", "Run analysis"),
    ("GET", "/api/v1/analysis", "List analysis runs"),
    ("GET", "/api/v1/insights", "List insights"),
]

# Probes are cached 60s and never raise (RequestException → "UNREACHABLE").
probed = cached_probe_endpoints(base, key, tuple(endpoints))
endpoint_data = [
    {"Method": method, "Path": path, "Description": desc, "Status": status}
    for (method, path, desc), (_m, _p, status) in zip(endpoints, probed)
]
st.dataframe(pd.DataFrame(endpoint_data), hide_index=True)

st.markdown("---")

# ─── Configuration ──────────────────────────────────────

st.subheader("Configuration")

with st.expander("Current Settings"):
    st.code(f"""
API Base URL:       {base}
Dashboard Port:     8501
Default Page:       Overview
    """, language="text")

st.markdown("---")

# ─── Connection Test ────────────────────────────────────

st.subheader("Connection Test")

if st.button("Test API Connection"):
    with st.spinner("Testing..."):
        start = time.time()
        # Deliberately NOT cached: this button measures live latency.
        test = get("/api/v1/health")
        elapsed = round((time.time() - start) * 1000)

    if test is not None and test.status_code == 200:
        st.success(f"Connected successfully ({elapsed}ms)")
    else:
        st.error(f"Connection failed ({elapsed}ms)")

st.markdown("---")

# ─── System Info ────────────────────────────────────────

st.subheader("System Information")

with st.expander("About Open Analytics AI"):
    st.markdown("""
    **Open Analytics AI** is a reusable analytics and AI interpretation platform.

    - **Backend**: FastAPI + Python
    - **Database**: PostgreSQL + SQLAlchemy
    - **Analytics**: Pandas, NumPy, SciPy, Scikit-learn
    - **AI**: Pluggable provider interface (Mock / Local LLM)
    - **Dashboard**: Streamlit (internal admin/testing)

    For developer integration docs, see `docs/developer-integration.md`.
    """)
