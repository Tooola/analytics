"""System page — API status, database status, AI provider, and logs."""

from __future__ import annotations

import os
import requests
import streamlit as st
import time
from datetime import datetime

st.title("System")
st.markdown("Monitor API health, database connectivity, AI provider status, and recent activity.")

def _clean_api_url(url: str) -> str:
    if not url:
        return ""
    url = str(url).strip()
    if url.startswith("API_BASE_URL="):
        url = url[len("API_BASE_URL="):].strip()
    return url.rstrip("/")


def _get_api_base():
    raw = st.session_state.get("api_base") or os.environ.get("API_BASE_URL", "https://scintillating-kindness-production-d038.up.railway.app")
    return _clean_api_url(raw)



def _get(path: str):
    headers = {}
    key = st.session_state.get("api_key", "")
    if key:
        headers["X-API-Key"] = key
    try:
        return requests.get(f"{_get_api_base()}{path}", headers=headers, timeout=10)
    except requests.ConnectionError:
        return None


# ─── API Health ─────────────────────────────────────────

st.subheader("API Status")

health = _get("/api/v1/health")
if health and health.status_code == 200:
    h = health.json()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        status_icon = "🟢" if h["status"] == "healthy" else "🟡"
        st.metric("Status", f"{status_icon} {h['status'].title()}")
    with c2:
        db_icon = "🟢" if h["database"] == "connected" else "🔴"
        st.metric("Database", f"{db_icon} {h['database'].title()}")
    with c3:
        st.metric("AI Provider", h["ai_provider"])
    with c4:
        st.metric("Version", h["version"])

    st.caption(f"Last checked: {h.get('timestamp', 'N/A')}")
else:
    st.error("API is not reachable. Check that the backend is running.")

st.markdown("---")

# ─── API Endpoints ──────────────────────────────────────

st.subheader("API Endpoints")

endpoints = [
    ("GET", "/api/v1/health", "Health check"),
    ("GET", "/api/v1/applications", "List applications"),
    ("POST", "/api/v1/applications", "Register application"),
    ("GET", "/api/v1/datasets", "List datasets"),
    ("POST", "/api/v1/datasets", "Register dataset"),
    ("POST", "/api/v1/analyze", "Run analysis"),
    ("GET", "/api/v1/analysis", "List analysis runs"),
    ("GET", "/api/v1/insights", "List insights"),
]

endpoint_data = []
headers = {}
if st.session_state.get("api_key"):
    headers["X-API-Key"] = st.session_state.api_key

for method, path, desc in endpoints:
    full_url = f"{_get_api_base()}{path}"
    try:
        if method == "GET":
            r = requests.get(full_url, headers=headers, timeout=5)
            status_code = str(r.status_code)
        else:
            status_code = "N/A (POST)"
    except requests.ConnectionError:
        status_code = "UNREACHABLE"
    endpoint_data.append({"Method": method, "Path": path, "Description": desc, "Status": status_code})

import pandas as pd
st.dataframe(pd.DataFrame(endpoint_data), hide_index=True)

st.markdown("---")

# ─── Configuration ──────────────────────────────────────

st.subheader("Configuration")

with st.expander("Current Settings"):
    st.code(f"""
API Base URL:       {_get_api_base()}
Dashboard Port:     8501
Default Page:       Overview
    """, language="text")

st.markdown("---")

# ─── Connection Test ────────────────────────────────────

st.subheader("Connection Test")

if st.button("Test API Connection"):
    with st.spinner("Testing..."):
        start = time.time()
        test = _get("/api/v1/health")
        elapsed = round((time.time() - start) * 1000)

    if test and test.status_code == 200:
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
