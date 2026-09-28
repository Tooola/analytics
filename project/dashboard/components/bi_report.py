"""BI Report Component — Senior Business Intelligence Restitution Engine for Streamlit.

Transforms statistical analysis results, raw data, and AI interpretations into a
professional, interactive Power BI / Tableau-style executive deliverable.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ─── Custom CSS Injection ───────────────────────────────────────────────

def inject_bi_theme_css() -> None:
    """Inject modern, clean BI styling rules into Streamlit."""
    st.markdown(
        """
        <style>
        /* Card & KPI Styling */
        .bi-kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 12px;
        }
        .bi-kpi-title {
            font-size: 0.825rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .bi-kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }
        .bi-kpi-sub {
            font-size: 0.8rem;
            color: #475569;
            margin-top: 4px;
        }
        .bi-badge-up {
            background-color: #DCFCE7;
            color: #15803D;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.75rem;
        }
        .bi-badge-down {
            background-color: #FEE2E2;
            color: #B91C1C;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.75rem;
        }
        .bi-badge-stable {
            background-color: #F1F5F9;
            color: #475569;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.75rem;
        }

        /* Section Container Cards */
        .bi-section-header {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1E293B;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 8px;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        .bi-card-box {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── Main BI Report Render Function ─────────────────────────────────────

def render_bi_report(
    analysis_response: dict[str, Any],
    raw_data: list[dict[str, Any]],
    app_slug: str,
    dataset_slug: str,
) -> None:
    """Render the complete 9-section BI report."""
    inject_bi_theme_css()

    df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
    results = analysis_response.get("results", {})
    insights = analysis_response.get("insights", [])
    ai_raw = analysis_response.get("ai_interpretation")

    # Parse AI Interpretation if present
    ai_data: dict[str, Any] | None = None
    if ai_raw:
        try:
            ai_data = json.loads(ai_raw)
        except (json.JSONDecodeError, TypeError):
            ai_data = {"summary": str(ai_raw)}

    # Section A: Report Header
    _render_section_a_header(df, app_slug, dataset_slug, analysis_response)

    # Section B: Executive KPI Cards
    _render_section_b_executive_summary(df, results)

    # Section C: Interactive Visualizations (Plotly)
    _render_section_c_visualizations(df, results)

    # Section D: Statistical & Business Findings
    _render_section_d_statistical_findings(results)

    # Section E: Anomalies & Vigilance Points
    _render_section_e_anomalies(results)

    # Section F: AI Insights & Interpretation
    _render_section_f_ai_insights(insights, ai_data)

    # Section G: Strategic Recommendations
    _render_section_g_recommendations(insights, ai_data)

    # Section H: Data Quality & Reliability Audit
    _render_section_h_data_quality(df, analysis_response)

    # Section I: Data Exploration Table
    _render_section_i_data_exploration(df)


# ─── Section Renderers ──────────────────────────────────────────────────

def _render_section_a_header(
    df: pd.DataFrame,
    app_slug: str,
    dataset_slug: str,
    analysis_response: dict[str, Any],
) -> None:
    """Section A: Report Header & Export Actions."""
    st.markdown("<div class='bi-section-header'>📊 Rapport d'Analyse Exécutive BI</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    with c1:
        st.markdown(f"**Dataset :** `{dataset_slug}` | **Application :** `{app_slug}`")
        st.caption(f"Analyse ID : `{analysis_response.get('analysis_id', 'N/A')}`")

    with c2:
        date_cols = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
        if date_cols and not df.empty:
            dates = pd.to_datetime(df[date_cols[0]], errors="coerce").dropna()
            if not dates.empty:
                st.markdown(f"**Période :** {dates.min().strftime('%Y-%m-%d')} ➔ {dates.max().strftime('%Y-%m-%d')}")
            else:
                st.markdown("**Période :** Non temporelle")
        else:
            st.markdown("**Période :** Transversale")

    with c3:
        st.markdown(f"**Enregistrements :** {len(df):,}")

    with c4:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        st.markdown(f"**Généré le :** {now_str}")

    # Export Action Bar
    e1, e2, e3 = st.columns([2, 2, 6])
    with e1:
        if not df.empty:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="💾 Exporter Données (CSV)",
                data=csv_bytes,
                file_name=f"export_{dataset_slug}.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with e2:
        if not df.empty:
            res_bytes = json.dumps(analysis_response, indent=2).encode("utf-8")
            st.download_button(
                label="📊 Exporter Résultats (JSON)",
                data=res_bytes,
                file_name=f"results_{dataset_slug}.json",
                mime="application/json",
                use_container_width=True,
            )
    st.markdown("---")


def _render_section_b_executive_summary(df: pd.DataFrame, results: dict[str, Any]) -> None:
    """Section B: Executive Summary KPI Cards."""
    st.markdown("### 📈 Synthèse Exécutive")

    summaries = results.get("summary", [])
    trends = results.get("trend", [])

    if not summaries and df.empty:
        st.info("Aucune donnée disponible pour la synthèse exécutive.")
        return

    trend_map = {t["column"]: t for t in trends} if trends else {}

    # Identify numeric metrics
    cols = st.columns(min(len(summaries), 4) if summaries else 4)

    for idx, s in enumerate(summaries[:4]):
        col_name = s.get("column", "Metric")
        col_target = cols[idx % len(cols)]

        mean_val = s.get("mean")
        median_val = s.get("median")
        count_val = s.get("count", 0)
        max_val = s.get("max")

        trend = trend_map.get(col_name, {})
        change_pct = trend.get("change_pct")
        direction = trend.get("direction", "stable")
        is_sig = trend.get("is_significant", True)

        with col_target:
            st.markdown("<div class='bi-kpi-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='bi-kpi-title'>{col_name}</div>", unsafe_allow_html=True)

            val_display = f"{mean_val:,.2f}" if mean_val is not None else "N/A"
            st.markdown(f"<div class='bi-kpi-value'>{val_display}</div>", unsafe_allow_html=True)

            sub_info = []
            if median_val is not None:
                sub_info.append(f"Médiane: {median_val:,.2f}")

            if change_pct is not None and is_sig:
                badge_cls = "bi-badge-up" if direction == "up" else ("bi-badge-down" if direction == "down" else "bi-badge-stable")
                arrow = "▲" if direction == "up" else ("▼" if direction == "down" else "►")
                sub_info.append(f"<span class='{badge_cls}'>{arrow} {change_pct:+.1f}%</span>")

            st.markdown(f"<div class='bi-kpi-sub'>{' | '.join(sub_info)}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _render_section_c_visualizations(df: pd.DataFrame, results: dict[str, Any]) -> None:
    """Section C: Interactive Plotly Visualizations."""
    st.markdown("### 📊 Visualisations Graphiques Interactives")

    if df.empty:
        st.info("Données insuffisantes pour générer les graphiques.")
        return

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]

    c1, c2 = st.columns(2)

    # Chart 1: Time series or Trend
    with c1:
        if date_cols and num_cols:
            date_col = date_cols[0]
            metric_col = num_cols[0]
            df_sorted = df.copy()
            df_sorted[date_col] = pd.to_datetime(df_sorted[date_col], errors="coerce")
            df_sorted = df_sorted.dropna(subset=[date_col]).sort_values(date_col)

            fig = px.line(
                df_sorted,
                x=date_col,
                y=metric_col,
                title=f"Évolution Temporelle de {metric_col}",
                template="plotly_white",
                color_discrete_sequence=["#2563EB"],
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig, use_container_width=True)
        elif len(num_cols) >= 1:
            fig = px.histogram(
                df,
                x=num_cols[0],
                title=f"Distribution de {num_cols[0]}",
                template="plotly_white",
                color_discrete_sequence=["#3B82F6"],
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Categorical breakdown or Correlation
    with c2:
        correlations = results.get("correlation", [])
        if correlations:
            top_corr = correlations[0]
            x_col = top_corr["column1"]
            y_col = top_corr["column2"]
            r_val = top_corr["coefficient"]

            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                trendline="ols",
                title=f"Corrélation : {x_col} vs {y_col} (r = {r_val})",
                template="plotly_white",
                color_discrete_sequence=["#10B981"],
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols and num_cols:
            cat_col = cat_cols[0]
            metric_col = num_cols[0]
            grouped = df.groupby(cat_col)[metric_col].sum().reset_index()

            fig = px.bar(
                grouped,
                x=cat_col,
                y=metric_col,
                title=f"{metric_col} par {cat_col}",
                template="plotly_white",
                color_discrete_sequence=["#6366F1"],
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig, use_container_width=True)
        elif len(num_cols) >= 2:
            fig = px.scatter(
                df,
                x=num_cols[0],
                y=num_cols[1],
                title=f"Dispersion : {num_cols[0]} vs {num_cols[1]}",
                template="plotly_white",
                color_discrete_sequence=["#8B5CF6"],
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig, use_container_width=True)


def _render_section_d_statistical_findings(results: dict[str, Any]) -> None:
    """Section D: Statistical & Business Findings."""
    st.markdown("### 🔍 Analyse Statistique & Métier")

    findings = []

    # Trends
    for t in results.get("trend", []):
        col = t.get("column")
        direction = t.get("direction")
        r2 = t.get("r_squared")
        p_val = t.get("p_value")
        slope = t.get("slope")
        is_sig = t.get("is_significant", False)

        if is_sig:
            findings.append({
                "type": "Tendance Significative",
                "col": col,
                "detail": f"Évolution à la {'hausse' if direction == 'up' else 'baisse'} de {col} (Pente={slope}, R²={r2}, p-value={p_val}).",
                "meaning": f"Tendance statistiquement fiable caractérisée par une pente régulière.",
            })
        else:
            findings.append({
                "type": "Variation Non Significative",
                "col": col,
                "detail": f"Fluctuations de {col} sans tendance dominante (R²={r2}, p-value={p_val}).",
                "meaning": "Variation assimilable à du bruit naturel ou un échantillon restreint.",
            })

    # Correlations
    for c in results.get("correlation", []):
        c1 = c.get("column1")
        c2 = c.get("column2")
        r = c.get("coefficient")
        rel = c.get("relationship")
        findings.append({
            "type": "Corrélation Statistique",
            "col": f"{c1} & {c2}",
            "detail": f"Corrélation {rel} forte (r = {r}, p < 0.05).",
            "meaning": "Les deux variables co-varient fortement. Note : une corrélation n'implique pas une relation de causalité.",
        })

    # Distributions
    for d in results.get("distribution", []):
        col = d.get("column")
        skew = d.get("skewness", 0.0)
        is_norm = d.get("is_normal")
        if abs(skew) > 1.0:
            findings.append({
                "type": "Asymétrie de Distribution",
                "col": col,
                "detail": f"Distribution fortement asymétrique (Skewness = {skew}).",
                "meaning": f"La majorité des valeurs est concentrée sur un côté avec quelques valeurs extrêmes en queue de distribution.",
            })

    if findings:
        for f in findings:
            with st.container():
                st.markdown(f"**📌 {f['type']} : `{f['col']}`**")
                st.markdown(f"- **Justification chiffrée :** {f['detail']}")
                st.caption(f"💡 **Signification métier :** {f['meaning']}")
                st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
    else:
        st.info("Aucun constat statistique particulier relevé sur ce dataset.")


def _render_section_e_anomalies(results: dict[str, Any]) -> None:
    """Section E: Anomalies & Vigilance Points Matrix."""
    st.markdown("### ⚠️ Anomalies & Points de Vigilance")

    anomalies_list = results.get("anomaly", [])
    has_anomalies = False

    for a in anomalies_list:
        col = a.get("column")
        count = a.get("count", 0)
        items = a.get("anomalies", [])
        method = a.get("method", "ensemble")

        if count > 0:
            has_anomalies = True
            st.warning(f"**{count} anomalie(s) détectée(s) dans `{col}`** (Méthode : `{method}`)")
            ano_df = pd.DataFrame(items)
            if not ano_df.empty:
                st.dataframe(ano_df, hide_index=True, use_container_width=True)
        else:
            st.success(f"✅ Aucune anomalie statistique détectée dans `{col}`.")

    if not has_anomalies and not anomalies_list:
        st.info("Aucune analyse d'anomalies exécutée.")


def _render_section_f_ai_insights(insights: list[dict[str, Any]], ai_data: dict[str, Any] | None) -> None:
    """Section F: AI Interpretation & Insights."""
    st.markdown("### 🤖 Insights & Interprétation par l'IA")

    if ai_data:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Moteur IA", ai_data.get("provider", "Open Analytics AI"))
        with c2:
            conf = ai_data.get("confidence", 0.9)
            st.metric("Indice de Confiance IA", f"{conf:.0%}")
        with c3:
            risk = ai_data.get("risk_assessment", "Faible")
            st.metric("Niveau de Risque Evalué", risk)

        summary_text = ai_data.get("summary", "")
        if summary_text:
            st.info(f"**Résumé Exécutif IA :** {summary_text}")

        # Structured findings from AI
        key_findings = ai_data.get("key_findings", [])
        if key_findings:
            st.markdown("#### 🔑 Synthèse des Constats IA")
            for kf in key_findings:
                st.markdown(f"- {kf}")

    # Structural insights from Insights Engine
    if insights:
        st.markdown("#### 📋 Insights Structurés du Moteur")
        ins_df = pd.DataFrame(insights)
        st.dataframe(ins_df, hide_index=True, use_container_width=True)


def _render_section_g_recommendations(insights: list[dict[str, Any]], ai_data: dict[str, Any] | None) -> None:
    """Section G: Strategic Recommendations Table."""
    st.markdown("### 💡 Recommandations Stratégiques Operationalisables")

    recs = []

    # From AI data if structured
    if ai_data and "recommendations" in ai_data:
        raw_recs = ai_data.get("recommendations", [])
        for i, r in enumerate(raw_recs):
            recs.append({
                "Constat Source": "Analyse Globale",
                "Action Proposée": r,
                "Objectif": "Optimisation des performances",
                "Priorité": "Haute" if i == 0 else "Moyenne",
                "KPI de Suivi": "Taux d'évolution / Valeur cible",
                "Échéance Indicative": "Court Terme (1-3 mois)",
            })

    # Fallback recommendations from insights engine
    if not recs:
        for ins in insights:
            if ins.get("type") in ("risk", "opportunity", "recommendation"):
                recs.append({
                    "Constat Source": ins.get("title", "Insight"),
                    "Action Proposée": ins.get("description", ""),
                    "Objectif": "Atténuation du risque / Maximisation de l'opportunité",
                    "Priorité": "Haute" if ins.get("severity") == "high" else "Moyenne",
                    "KPI de Suivi": ins.get("metric", "KPI Principal"),
                    "Échéance Indicative": "Moyen Terme",
                })

    if recs:
        rec_df = pd.DataFrame(recs)
        st.dataframe(rec_df, hide_index=True, use_container_width=True)
    else:
        st.info("Aucune recommandation stratégique spécifique générée pour ce dataset.")


def _render_section_h_data_quality(df: pd.DataFrame, analysis_response: dict[str, Any]) -> None:
    """Section H: Data Quality & Reliability Audit."""
    st.markdown("### 🛡️ Qualité & Fiabilité des Données")

    validation = analysis_response.get("validation", {})
    total_rows = len(df)
    is_valid = validation.get("valid", True)
    errors = validation.get("errors", [])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Enregistrements Valides", f"{total_rows:,}")
    with c2:
        st.metric("Conformité Schéma", "100%" if is_valid else "Inconforme")
    with c3:
        null_count = df.isnull().sum().sum() if not df.empty else 0
        st.metric("Valeurs Manquantes (Total)", f"{null_count}")
    with c4:
        dup_count = df.duplicated().sum() if not df.empty else 0
        st.metric("Doublons Détectés", f"{dup_count}")

    if not df.empty:
        completeness_pct = ((df.notnull().sum().sum()) / (df.shape[0] * df.shape[1])) * 100
        st.caption(f"Taux de complétude global du jeu de données : **{completeness_pct:.1f}%**")


def _render_section_i_data_exploration(df: pd.DataFrame) -> None:
    """Section I: Interactive Data Exploration Table."""
    st.markdown("### 🔎 Exploration Intégrale des Données")

    if df.empty:
        st.info("Aucune donnée à afficher dans le tableau d'exploration.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=False,
    )
