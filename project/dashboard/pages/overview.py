"""Overview page — system summary and KPIs."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# dashboard/ on sys.path → share the central API client (PLAN.md V4)
_DASHBOARD_DIR = Path(__file__).resolve().parent.parent
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

from api_client import cached_get, cached_health, get_api_base  # noqa: E402

st.title("Overview")
st.markdown("Platform-wide summary and health status.")

base = get_api_base()
key = st.session_state.get("api_key", "")

col1, col2, col3, col4 = st.columns(4)

# Counts — cached 60s (V5): one probe per endpoint per minute, not per rerun.
app_data = cached_get(base, key, "/api/v1/applications")
ds_data = cached_get(base, key, "/api/v1/datasets")
an_data = cached_get(base, key, "/api/v1/analysis")
ins_data = cached_get(base, key, "/api/v1/insights")

app_count = len(app_data) if isinstance(app_data, list) else 0
ds_count = len(ds_data) if isinstance(ds_data, list) else 0
an_count = len(an_data) if isinstance(an_data, list) else 0
ins_count = len(ins_data) if isinstance(ins_data, list) else 0

with col1:
    st.metric("Applications", app_count)
with col2:
    st.metric("Datasets", ds_count)
with col3:
    st.metric("Analyses Run", an_count)
with col4:
    st.metric("Insights", ins_count)

st.markdown("---")

# Health detail (shared 30s cache with the sidebar probe)
h = cached_health(base, key)
if h and h.get("status"):
    st.subheader("System Health")
    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        st.metric("Status", str(h["status"]).title())
    with hc2:
        st.metric("Database", str(h.get("database", "?")).title())
    with hc3:
        st.metric("AI Provider", str(h.get("ai_provider", "?")))
    st.caption(f"Version {h.get('version', '?')} | {h.get('timestamp', '?')}")
else:
    st.warning("API is not reachable.")

# Recent analyses
st.markdown("---")
st.subheader("Recent Analyses")
if isinstance(an_data, list):
    runs = an_data
    if runs:
        import pandas as pd

        df = pd.DataFrame(runs)
        display_cols = [c for c in ["id", "status", "row_count", "created_at"] if c in df.columns]
        st.dataframe(df[display_cols], hide_index=True)
    else:
        st.info("No analyses have been run yet.")
