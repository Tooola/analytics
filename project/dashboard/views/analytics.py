"""Analytics page — run analyses and visualize results."""

from __future__ import annotations

import json

import pandas as pd
import sys
import streamlit as st
from pathlib import Path

dashboard_dir = Path(__file__).parent.parent
project_dir = dashboard_dir.parent
for d in (str(dashboard_dir), str(project_dir)):
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from components.bi_report import render_bi_report
except ModuleNotFoundError as e:
    if e.name and ("components" in e.name or "dashboard" in e.name):
        from dashboard.components.bi_report import render_bi_report
    else:
        raise



from api_client import get as _get  # noqa: E402
from api_client import get_api_base as _get_api_base
from api_client import post as _post


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
    ["summary", "trend", "anomaly", "correlation", "distribution", "forecast"],
    default=["summary", "trend", "anomaly", "correlation", "distribution", "forecast"],
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
            r = post(
                "/api/v1/analyze",
                json_data={
                    "application": selected_app,
                    "dataset": selected_ds,
                    "analysis": analysis_types,
                    "data": data,
                    "include_ai": include_ai,
                },
                headers={"X-API-Key": api_key},
                timeout=60,
            )
            if r is None:
                st.error(f"Cannot reach API at {_get_api_base()}.")
                st.stop()

            if r.status_code == 200:
                result = r.json()
                if not result["success"]:
                    st.error("Data validation failed.")
                    st.json(result["validation"])
                    st.stop()

                st.success("Analyse terminée avec succès !")
                render_bi_report(result, data, selected_app, selected_ds)

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
