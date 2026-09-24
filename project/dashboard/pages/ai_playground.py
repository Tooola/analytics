"""Insight Studio & Schema Sandbox — Bac à sable de validation et d'analyse IA."""

from __future__ import annotations

import json

import pandas as pd
import requests as _r
import streamlit as st


import os


def _get_api_base():
    return st.session_state.get("api_base") or os.environ.get("API_BASE_URL", "https://scintillating-kindness-production-d038.up.railway.app")



def _get(path):
    headers = {}
    key = st.session_state.get("api_key", "")
    if key:
        headers["X-API-Key"] = key
    try:
        return _r.get(f"{_get_api_base()}{path}", headers=headers, timeout=10)
    except _r.ConnectionError:
        return None


st.title("⚡ Insight Studio & API Sandbox")
st.markdown("Banc d'essai d'API pour les développeurs et décideurs : Validation de schémas, tests de charge et simulation d'inférence IA en direct.")


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

    api_target = _get_api_base()
    with st.spinner("Running analytics + AI interpretation..."):
        try:
            r = _r.post(
                f"{api_target}/api/v1/analyze",
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
            st.error(f"Cannot reach API at {api_target}. Is the backend running?")
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

    st.subheader("4. 🤖 Interprétation IA & Rapport")
    if result.get("ai_interpretation"):
        try:
            ai = json.loads(result["ai_interpretation"])

            # ── Métriques d'en-tête ──────────────────────────
            col_m1, col_m2, col_m3 = st.columns(3)
            risk = ai.get("risk_assessment", "")
            confidence = ai.get("confidence", 0)
            with col_m1:
                st.metric("🧠 Provider", ai.get("provider", "IA"))
            with col_m2:
                st.metric("📊 Confiance", f"{confidence:.0%}")
            with col_m3:
                risk_label = "🔴 Élevé" if "Élevé" in risk or "Critique" in risk or "High" in risk \
                    else ("🟡 Modéré" if "Modéré" in risk or "Moderate" in risk else "🟢 Faible")
                st.metric("⚠️ Risque", risk_label)

            st.markdown("---")

            # ── Résumé exécutif ──────────────────────────────
            with st.container(border=True):
                st.markdown("### 📋 Résumé Exécutif")
                st.info(ai.get("summary", ""))

            # ── Évaluation des risques ───────────────────────
            if risk:
                with st.container(border=True):
                    st.markdown("### ⚡ Évaluation des Risques")
                    if "Élevé" in risk or "Critique" in risk or "High" in risk:
                        st.error(f"**{risk}**")
                    elif "Modéré" in risk or "Moderate" in risk:
                        st.warning(f"**{risk}**")
                    else:
                        st.success(f"**{risk}**")

            # ── Corps du rapport ─────────────────────────────
            col_a, col_b = st.columns(2)
            with col_a:
                with st.container(border=True):
                    st.markdown("### 🔍 Constats Clés")
                    findings = ai.get("key_findings", [])
                    if findings:
                        for i, f in enumerate(findings, 1):
                            st.markdown(f"**{i}.** {f}")
                    else:
                        st.caption("Aucun constat.")

                with st.container(border=True):
                    st.markdown("### 💡 Recommandations Stratégiques")
                    recs = ai.get("recommendations", [])
                    if recs:
                        for rec in recs:
                            st.markdown(f"✅ {rec}")
                    else:
                        st.caption("Aucune recommandation.")

            with col_b:
                with st.container(border=True):
                    st.markdown("### 🛠️ Plan d'Action Priorisé")
                    plans = ai.get("action_plan", [])
                    if plans:
                        for act in plans:
                            if "IMMÉDIAT" in act.upper() or "🔴" in act:
                                st.error(act)
                            elif "COURT TERME" in act.upper() or "🟡" in act:
                                st.warning(act)
                            elif "LONG TERME" in act.upper() or "🟢" in act:
                                st.success(act)
                            else:
                                st.markdown(f"▶️ {act}")
                    else:
                        st.caption("Aucun plan d'action.")

        except (json.JSONDecodeError, TypeError):
            st.text(result["ai_interpretation"])
    else:
        st.caption("No AI interpretation was returned.")

    st.caption(f"Analysis ID: {result['analysis_id']}")
