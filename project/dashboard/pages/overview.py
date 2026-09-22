"""Overview page — system summary and KPIs."""

from __future__ import annotations

import requests as _r
import streamlit as st

st.title("Overview")
st.markdown("Platform-wide summary and health status.")

# Health
resp = st.session_state_api_get() if hasattr(st, "session_state_api_get") else None

# Use the helper from app.py
DEFAULT_API = "https://scintillating-kindness-production-d038.up.railway.app"
API = st.session_state.get("api_base")
if not API or API in ["http://localhost:8000", "http://127.0.0.1:8000"]:
    API = DEFAULT_API


def _get(path):
    headers = {}
    key = st.session_state.get("api_key", "")
    if key:
        headers["X-API-Key"] = key
    try:
        return _r.get(f"{API}{path}", headers=headers, timeout=10)
    except _r.ConnectionError:
        return None


col1, col2, col3, col4 = st.columns(4)

# Applications count
apps_resp = _get("/api/v1/applications")
app_count = len(apps_resp.json()) if apps_resp and apps_resp.status_code == 200 else 0

# Datasets count
ds_resp = _get("/api/v1/datasets")
ds_count = len(ds_resp.json()) if ds_resp and ds_resp.status_code == 200 else 0

# Analyses count
an_resp = _get("/api/v1/analysis")
an_count = len(an_resp.json()) if an_resp and an_resp.status_code == 200 else 0

# Insights count
ins_resp = _get("/api/v1/insights")
ins_count = len(ins_resp.json()) if ins_resp and ins_resp.status_code == 200 else 0

with col1:
    st.metric("Applications", app_count)
with col2:
    st.metric("Datasets", ds_count)
with col3:
    st.metric("Analyses Run", an_count)
with col4:
    st.metric("Insights", ins_count)

st.markdown("---")

# Health detail
health = _get("/api/v1/health")
if health and health.status_code == 200:
    h = health.json()
    st.subheader("System Health")
    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        st.metric("Status", h["status"].title())
    with hc2:
        st.metric("Database", h["database"].title())
    with hc3:
        st.metric("AI Provider", h["ai_provider"])
    st.caption(f"Version {h['version']} | {h['timestamp']}")
else:
    st.warning("API is not reachable.")

# Recent analyses
st.markdown("---")
st.subheader("Recent Analyses")
if an_resp and an_resp.status_code == 200:
    runs = an_resp.json()
    if runs:
        import pandas as pd
        df = pd.DataFrame(runs)
        display_cols = [c for c in ["id", "status", "row_count", "created_at"] if c in df.columns]
        st.dataframe(df[display_cols], hide_index=True)
    else:
        st.info("No analyses have been run yet.")
