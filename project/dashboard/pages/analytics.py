"""Analytics page — run analyses and visualize results."""

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


st.title("Analytics")
st.markdown("Select an application and dataset, then run an analysis.")

# ─── Selectors ─────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    apps_resp = _get("/api/v1/applications")
    apps = apps_resp.json() if apps_resp and apps_resp.status_code == 200 else []
    app_options = {a["slug"]: a for a in apps}

    if not app_options:
        st.warning("Aucune application enregistrée. Allez dans **Applications** pour en créer une.")
        selected_app = "—"
    else:
        selected_app = st.selectbox("Application", list(app_options.keys()))

with col2:
    if selected_app and selected_app != "—":
        ds_resp = _get(f"/api/v1/datasets/by-app/{selected_app}")
        datasets = ds_resp.json() if ds_resp and ds_resp.status_code == 200 else []
    else:
        datasets = []

    if not datasets and selected_app and selected_app != "—":
        st.warning(
            f"Aucun dataset pour **{selected_app}**. "
            "Enregistrez-en un dans la page **Datasets** (menu de gauche)."
        )
        selected_ds = "—"
    else:
        ds_options = {d["slug"]: d for d in datasets}
        selected_ds = st.selectbox("Dataset", list(ds_options.keys()) if ds_options else ["—"])

# ─── Analysis type selection ───────────────────────────

analysis_types = st.multiselect(
    "Analysis Types",
    ["summary", "trend", "anomaly"],
    default=["summary"],
)

include_ai = st.checkbox("Inclure l'interprétation automatique", value=False)

# ─── API Key input ─────────────────────────────────────

api_key = st.text_input(
    "Clé API (X-API-Key) — doit correspondre à l'application sélectionnée",
    value=st.session_state.get("api_key", ""),
    type="password",
    placeholder="anal_...",
)
if api_key:
    st.session_state["api_key"] = api_key

st.markdown("---")

# ─── Data input ────────────────────────────────────────

st.subheader("Data Input")

if selected_ds != "—" and datasets:
    ds_options_full = {d["slug"]: d for d in datasets}
    ds = ds_options_full.get(selected_ds, {})
    fields = ds.get("fields", [])
    if fields:
        st.caption(f"Champs attendus : {', '.join(f['name'] for f in fields)}")

input_mode = st.radio("Input Mode", ["Paste JSON", "Upload CSV"])

data: list[dict] = []

if input_mode == "Paste JSON":
    json_text = st.text_area(
        "Paste data as JSON array",
        height=200,
        placeholder='[{"field1": 123, "field2": "abc"}, ...]',
    )
    if json_text:
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
else:
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            data = df.to_dict("records")
            st.success(f"Loaded {len(data)} rows from CSV.")
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")

# ─── Run analysis ──────────────────────────────────────

if st.button("Lancer l'analyse", type="primary"):
    if not selected_app or selected_app == "—":
        st.warning("Veuillez sélectionner une application.")
    elif not selected_ds or selected_ds == "—":
        st.warning("Veuillez sélectionner un dataset. Si l'application n'en a pas, enregistrez-en un dans la page **Datasets**.")
    elif not analysis_types:
        st.warning("Veuillez sélectionner au moins un type d'analyse.")
    elif not data:
        st.warning("Veuillez fournir des données à analyser.")
    elif not api_key:
        st.warning("Veuillez saisir une clé API correspondant à l'application sélectionnée.")
    else:
        with st.spinner("Running analysis..."):
            try:
                r = _r.post(
                    f"{API}/api/v1/analyze",
                    json={
                        "application": selected_app,
                        "dataset": selected_ds,
                        "analysis": analysis_types,
                        "data": data,
                        "include_ai": include_ai,
                    },
                    headers={"X-API-Key": api_key},
                    timeout=60,
                )
            except _r.ConnectionError:
                st.error("Cannot reach API.")
                st.stop()

            if r.status_code == 200:
                result = r.json()
                if not result["success"]:
                    st.error("Data validation failed.")
                    st.json(result["validation"])
                    st.stop()

                st.success("Analysis completed!")

                # Summary
                results = result.get("results", {})
                if results.get("summary"):
                    st.subheader("Summary Statistics")
                    summary_df = pd.DataFrame(results["summary"])
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)

                # Trend
                if results.get("trend"):
                    st.subheader("Trend Analysis")
                    trend_df = pd.DataFrame(results["trend"])
                    st.dataframe(trend_df, use_container_width=True, hide_index=True)

                # Anomaly
                if results.get("anomaly"):
                    st.subheader("Anomaly Detection")
                    for a in results["anomaly"]:
                        if a["count"] > 0:
                            st.warning(f"{a['count']} anomalies in **{a['column']}** (method: {a['method']})")
                            st.dataframe(pd.DataFrame(a["anomalies"]), hide_index=True)
                        else:
                            st.info(f"No anomalies in **{a['column']}**")

                # Insights
                insights = result.get("insights", [])
                if insights:
                    st.subheader("Insights")
                    for ins in insights:
                        st.markdown(f"**{ins['title']}**")
                        st.caption(ins["description"])
                        if ins.get("value") is not None:
                            st.caption(f"Value: {ins['value']} {ins.get('unit', '')} | Confidence: {ins['confidence']:.0%}")

                # AI interpretation
                if result.get("ai_interpretation"):
                    st.subheader("Interprétation & Recommandations")
                    try:
                        ai = json.loads(result["ai_interpretation"])
                        st.markdown(f"**Provider:** `{ai.get('provider', '—')}` | **Confidence:** `{ai.get('confidence', 0):.0%}`")
                        if ai.get("risk_assessment"):
                            st.info(f"**Évaluation des risques :** {ai['risk_assessment']}")
                        st.markdown("---")
                        st.markdown(f"### Executive Summary\n{ai.get('summary', '')}")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if ai.get("key_findings"):
                                st.markdown("#### Constats clés")
                                for f in ai["key_findings"]:
                                    st.markdown(f"- {f}")

                            if ai.get("recommendations"):
                                st.markdown("#### Recommandations stratégiques")
                                for rec in ai["recommendations"]:
                                    st.markdown(f"- {rec}")

                        with col_b:
                            if ai.get("action_plan"):
                                st.markdown("#### Plan d'action & Solutions")
                                for act in ai["action_plan"]:
                                    st.markdown(f"- {act}")
                    except (json.JSONDecodeError, TypeError):
                        st.text(result["ai_interpretation"])

                # Analysis ID
                st.caption(f"Analysis ID: {result['analysis_id']}")
            elif r.status_code == 401:
                st.error("Invalid API key.")
            elif r.status_code == 403:
                st.error("API key does not match the selected application.")
            elif r.status_code == 404:
                st.error("Application or dataset not found.")
            else:
                st.error(f"Analysis failed (HTTP {r.status_code})")
                try:
                    st.json(r.json())
                except Exception:
                    st.text(r.text)
