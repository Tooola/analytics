"""Quick Test — Analyse instantanée sans créer d'application ni de dataset.

Colle n'importe quel JSON, clique sur Analyser.
Idéal pour tester rapidement le moteur analytique depuis le dashboard admin.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_DASHBOARD_DIR = Path(__file__).resolve().parent.parent
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

from api_client import get_api_base as _get_api_base  # noqa: E402
from api_client import post  # noqa: E402

# ─── Add import for bi_report renderer ──────────────────
try:
    from components.bi_report import render_bi_report
except ModuleNotFoundError:
    from dashboard.components.bi_report import render_bi_report

# ─────────────────────────────────────────────────────────

st.title("⚡ Quick Test — Analyse JSON Instantanée")
st.markdown(
    "**Pas besoin de créer une application ou un dataset.** "
    "Collez votre JSON, choisissez les analyses, cliquez — le moteur s'occupe du reste."
)

st.info(
    "💡 **Mode Admin uniquement.** Cet endpoint ne nécessite pas de clé API. "
    "Les colonnes et types de données sont détectés automatiquement depuis votre JSON."
)

# ─── Sample data helper ───────────────────────────────────

SAMPLE_JSON = json.dumps([
    {"date": "2026-09-01", "produit": "Maïs", "quantite": 4500, "prix_unitaire": 0.18, "region": "Nord"},
    {"date": "2026-09-02", "produit": "Blé",  "quantite": 3200, "prix_unitaire": 0.22, "region": "Sud"},
    {"date": "2026-09-03", "produit": "Soja",  "quantite": 5100, "prix_unitaire": 0.35, "region": "Est"},
    {"date": "2026-09-04", "produit": "Maïs", "quantite": 4650, "prix_unitaire": 0.18, "region": "Nord"},
    {"date": "2026-09-05", "produit": "Tournesol", "quantite": 2800, "prix_unitaire": 0.45, "region": "Ouest"},
    {"date": "2026-09-06", "produit": "Blé",  "quantite": 3400, "prix_unitaire": 0.22, "region": "Sud"},
    {"date": "2026-09-07", "produit": "Soja",  "quantite": 12000, "prix_unitaire": 0.35, "region": "Est"},
    {"date": "2026-09-08", "produit": "Maïs", "quantite": 4800, "prix_unitaire": 0.18, "region": "Nord"},
], indent=2)

# ─── Input ────────────────────────────────────────────────

col_left, col_right = st.columns([3, 1])

with col_right:
    if st.button("📋 Charger exemple", use_container_width=True):
        st.session_state["qt_json"] = SAMPLE_JSON

    label = st.text_input("Label (optionnel)", value="test-admin", placeholder="mon-test")
    analysis_types = st.multiselect(
        "Analyses",
        ["summary", "trend", "anomaly", "correlation", "distribution", "forecast"],
        default=["summary", "trend", "anomaly"],
    )
    include_ai = st.checkbox("🤖 Interprétation IA (Groq)", value=True)
    st.markdown("---")
    run_button = st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True)

with col_left:
    json_text = st.text_area(
        "📥 Données JSON (tableau d'objets)",
        value=st.session_state.get("qt_json", ""),
        height=320,
        placeholder='[{"date": "2026-01-01", "ventes": 1000, "region": "Nord"}, ...]',
        key="qt_json_area",
    )

# ─── Parse ────────────────────────────────────────────────

data: list[dict] = []
parse_error = None
if json_text:
    try:
        parsed = json.loads(json_text)
        if isinstance(parsed, list):
            data = parsed
        elif isinstance(parsed, dict):
            # Single object → wrap in list
            data = [parsed]
        else:
            parse_error = "Le JSON doit être un tableau d'objets [ {...}, {...} ]"
    except json.JSONDecodeError as e:
        parse_error = f"JSON invalide : {e}"

if parse_error:
    st.error(parse_error)
elif data:
    st.caption(f"✅ {len(data)} enregistrements chargés — {len(data[0])} colonnes détectées : `{', '.join(str(k) for k in data[0].keys())}`")

# ─── Run ──────────────────────────────────────────────────

if run_button:
    if not data:
        st.warning("Veuillez coller des données JSON valides.")
        st.stop()
    if not analysis_types:
        st.warning("Sélectionnez au moins un type d'analyse.")
        st.stop()

    with st.spinner("Analyse en cours..."):
        resp = post(
            "/api/v1/analyze/quick",
            json_data={
                "data": data,
                "analysis": analysis_types,
                "include_ai": include_ai,
                "label": label or "test-admin",
            },
            timeout=90,
        )

    if resp is None:
        st.error(f"❌ Impossible de contacter l'API à `{_get_api_base()}`. Vérifiez que le backend est en ligne.")
        st.stop()

    if resp.status_code != 200:
        st.error(f"❌ Erreur API (HTTP {resp.status_code})")
        try:
            st.json(resp.json())
        except Exception:
            st.text(resp.text)
        st.stop()

    result = resp.json()

    # Cache result
    st.session_state["qt_result"] = {
        "result": result,
        "data": data,
        "label": label or "test-admin",
    }
    st.rerun()

# ─── Display results ─────────────────────────────────────

_cached = st.session_state.get("qt_result")
if _cached:
    result = _cached["result"]
    raw_data = _cached["data"]
    _label = _cached["label"]

    st.success(f"✅ Analyse terminée — {result.get('row_count', 0)} enregistrements traités")

    # Show inferred fields
    with st.expander("🔍 Colonnes détectées automatiquement"):
        fields_df = pd.DataFrame(result.get("fields_inferred", []))
        if not fields_df.empty:
            st.dataframe(fields_df, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Adapt result format for bi_report renderer
    adapted_result = {
        "success": True,
        "analysis_id": _label,
        "application": _label,
        "dataset": _label,
        "validation": {"valid": True, "errors": [], "row_count": len(raw_data)},
        "results": result.get("results", {}),
        "insights": result.get("insights", []),
        "ai_interpretation": result.get("ai_interpretation"),
    }
    render_bi_report(adapted_result, raw_data, _label, _label)

    if st.button("🗑️ Effacer les résultats", key="clear_qt"):
        st.session_state.pop("qt_result", None)
        st.rerun()
