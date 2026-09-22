"""AI Playground — test the full Raw Data → Analytics → Context → AI pipeline."""

from __future__ import annotations

import json

import pandas as pd
import requests as _r
import streamlit as st

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


st.title("AI Playground")
st.markdown("Test the full pipeline: Raw Data → Analytics → Analytical Context → AI Interpretation")

st.markdown("""
1. Select an application and dataset
2. Provide data
3. Run analysis with AI enabled
4. See the sanitized context and AI interpretation side by side
""")

# ─── Selectors ─────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    apps_resp = _get("/api/v1/applications")
    apps = apps_resp.json() if apps_resp and apps_resp.status_code == 200 else []
    app_options = {a["slug"]: a for a in apps}
    selected_app = st.selectbox("Application", list(app_options.keys()) if app_options else ["—"])

with col2:
    if selected_app != "—":
        ds_resp = _get(f"/api/v1/datasets/by-app/{selected_app}")
        datasets = ds_resp.json() if ds_resp and ds_resp.status_code == 200 else []
    else:
        datasets = []
    ds_options = {d["slug"]: d for d in datasets}
    selected_ds = st.selectbox("Dataset", list(ds_options.keys()) if ds_options else ["—"])

api_key = st.text_input("API Key", value=st.session_state.get("api_key", ""), type="password", placeholder="anal_...")
if api_key:
    st.session_state["api_key"] = api_key

st.markdown("---")

# ─── Data input ────────────────────────────────────────

st.subheader("1. Raw Data")

if selected_ds != "—" and ds_options:
    ds = ds_options[selected_ds]
    fields = ds.get("fields", [])
    st.caption(f"Expected fields: {', '.join(f['name'] for f in fields)}")

json_text = st.text_area(
    "Paste data as JSON array",
    height=150,
    placeholder='[{"date": "2024-01-01", "revenue": 1000, "cost": 500}, ...]',
)

data = []
if json_text:
    try:
        data = json.loads(json_text)
        st.caption(f"{len(data)} rows loaded.")
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")

st.markdown("---")

# ─── Run ───────────────────────────────────────────────

if st.button("Run Full Pipeline", type="primary"):
    current_key = api_key or st.session_state.get("api_key", "")
    if not all([selected_app != "—", selected_ds != "—", data, current_key]):
        st.warning("Please select Application, Dataset, provide Data, and ensure API Key is provided.")
        st.stop()

    API = st.session_state.get("api_base", "http://127.0.0.1:8000")
    with st.spinner("Running analytics + AI interpretation..."):
        try:
            r = _r.post(
                f"{API}/api/v1/analyze",
                json={
                    "application": selected_app,
                    "dataset": selected_ds,
                    "analysis": ["summary", "trend", "anomaly"],
                    "data": data,
                    "include_ai": True,
                },
                headers={"X-API-Key": current_key},
                timeout=60,
            )
        except _r.ConnectionError:
            st.error(f"Cannot reach API at {API}. Is the backend running?")
            st.stop()

    if r.status_code != 200:
        st.error(f"Request failed (HTTP {r.status_code})")
        try:
            st.json(r.json())
        except Exception:
            st.text(r.text)
        st.stop()

    result = r.json()
    if not result["success"]:
        st.error("Data validation failed.")
        st.json(result["validation"])
        st.stop()

    # ─── 2. Analytics Results ──────────────────────────

    st.subheader("2. Analytics Results")
    results = result.get("results", {})

    tab_sum, tab_trend, tab_anom = st.tabs(["Summary", "Trend", "Anomaly"])

    with tab_sum:
        if results.get("summary"):
            st.dataframe(pd.DataFrame(results["summary"]), use_container_width=True, hide_index=True)
        else:
            st.caption("No summary results.")

    with tab_trend:
        if results.get("trend"):
            st.dataframe(pd.DataFrame(results["trend"]), use_container_width=True, hide_index=True)
        else:
            st.caption("No trend results.")

    with tab_anom:
        if results.get("anomaly"):
            for a in results["anomaly"]:
                st.markdown(f"**{a['column']}** — {a['count']} anomaly/anomalies ({a['method']})")
                if a["count"]:
                    st.dataframe(pd.DataFrame(a["anomalies"]), hide_index=True)
        else:
            st.caption("No anomaly results.")

    # ─── 3. Analytical Context ─────────────────────────

    st.subheader("3. Analytical Context (sent to AI — no raw data)")
    st.info("This is what the AI provider receives. Notice: no individual data rows, only aggregated metrics.")

    context_demo = {
        "application": selected_app,
        "dataset": selected_ds,
        "row_count": len(data),
        "summary": results.get("summary", []),
        "trends": results.get("trend", []),
        "anomalies": results.get("anomaly", []),
        "insights": [{"type": i["type"], "title": i["title"], "severity": i["severity"]} for i in result.get("insights", [])],
    }
    st.json(context_demo)

    # ─── 4. AI Interpretation ──────────────────────────

    st.subheader("4. AI Interpretation & Solution Proposals")
    if result.get("ai_interpretation"):
        try:
            ai = json.loads(result["ai_interpretation"])
            st.markdown(f"**Provider:** `{ai.get('provider', '—')}` | **Confidence:** `{ai.get('confidence', 0):.0%}`")
            if ai.get("risk_assessment"):
                st.info(f"⚡ **Risk Assessment:** {ai['risk_assessment']}")
            st.markdown("---")
            st.markdown(f"### Executive Summary\n{ai.get('summary', '')}")

            col_a, col_b = st.columns(2)
            with col_a:
                if ai.get("key_findings"):
                    st.markdown("#### 📊 Key Findings")
                    for f in ai["key_findings"]:
                        st.markdown(f"- {f}")

                if ai.get("recommendations"):
                    st.markdown("#### 💡 Strategic Advice")
                    for rec in ai["recommendations"]:
                        st.markdown(f"- {rec}")

            with col_b:
                if ai.get("action_plan"):
                    st.markdown("#### 🛠️ Proposition de Solutions (Action Plan)")
                    for act in ai["action_plan"]:
                        st.markdown(f"- {act}")
        except (json.JSONDecodeError, TypeError):
            st.text(result["ai_interpretation"])
    else:
        st.caption("No AI interpretation was returned.")

    st.caption(f"Analysis ID: {result['analysis_id']}")
