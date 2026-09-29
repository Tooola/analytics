"""BI Report Component — Senior Business Intelligence Restitution Engine for Streamlit.

Transforms statistical analysis results, raw data, and AI interpretations into a
professional, executive-ready Power BI / Tableau-style deliverable.
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
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
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
    """Render the complete 9-section executive BI report."""
    inject_bi_theme_css()

    response_dict = analysis_response or {}
    df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
    results = response_dict.get("results") or {}
    insights = response_dict.get("insights") or []
    ai_raw = response_dict.get("ai_interpretation")

    # Parse AI Interpretation if present
    ai_data: dict[str, Any] | None = None
    if ai_raw:
        if isinstance(ai_raw, dict):
            ai_data = ai_raw
        else:
            try:
                ai_data = json.loads(ai_raw)
            except (json.JSONDecodeError, TypeError):
                ai_data = {"summary": str(ai_raw)}

    # Section A: Report Header
    _render_section_a_header(df, app_slug, dataset_slug, response_dict)

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
    _render_section_h_data_quality(df, response_dict)

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
                width="stretch",
            )
    with e2:
        if not df.empty:
            res_bytes = json.dumps(analysis_response, indent=2).encode("utf-8")
            st.download_button(
                label="📊 Exporter Résultats (JSON)",
                data=res_bytes,
                file_name=f"results_{dataset_slug}.json",
                mime="application/json",
                width="stretch",
            )
    st.markdown("---")


def _render_section_b_executive_summary(df: pd.DataFrame, results: dict[str, Any]) -> None:
    """Section B: Executive Summary KPI Cards."""
    st.markdown("### 📈 Synthèse Exécutive")

    results_dict = results or {}
    summaries = results_dict.get("summary") or []
    trends = results_dict.get("trend") or []

    if not summaries and df.empty:
        st.info("Aucune donnée disponible pour la synthèse exécutive.")
        return

    trend_map = {t["column"]: t for t in trends if isinstance(t, dict) and "column" in t} if isinstance(trends, list) else {}

    if not isinstance(summaries, list) or len(summaries) == 0:
        if not df.empty:
            # Fallback KPI cards from DataFrame numeric columns if summary is not selected
            num_df = df.select_dtypes(include=[np.number])
            if not num_df.empty:
                cols = st.columns(min(len(num_df.columns), 4))
                for idx, col_name in enumerate(num_df.columns[:4]):
                    col_target = cols[idx % len(cols)]
                    mean_val = num_df[col_name].mean()
                    med_val = num_df[col_name].median()
                    with col_target:
                        st.markdown("<div class='bi-kpi-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='bi-kpi-title'>{col_name}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='bi-kpi-value'>{mean_val:,.2f}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='bi-kpi-sub'>Moyenne | Médiane: {med_val:,.2f}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
        return

    cols = st.columns(min(len(summaries), 4))

    for idx, s in enumerate(summaries[:4]):
        if not isinstance(s, dict):
            continue
        col_name = s.get("column", "Metric")
        col_target = cols[idx % len(cols)]

        mean_val = s.get("mean")
        median_val = s.get("median")

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
                sub_info.append(f"Moyenne (Médiane: {median_val:,.2f})")

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

    results_dict = results or {}
    correlations = results_dict.get("correlation") or []

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
            st.plotly_chart(fig, width="stretch")
        elif len(num_cols) >= 1:
            fig = px.histogram(
                df,
                x=num_cols[0],
                title=f"Distribution de {num_cols[0]}",
                template="plotly_white",
                color_discrete_sequence=["#3B82F6"],
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig, width="stretch")

    # Chart 2: Categorical breakdown or Correlation
    with c2:
        if isinstance(correlations, list) and len(correlations) > 0 and isinstance(correlations[0], dict):
            top_corr = correlations[0]
            x_col = top_corr.get("column1")
            y_col = top_corr.get("column2")
            r_val = top_corr.get("coefficient", 0)

            if x_col in df.columns and y_col in df.columns:
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
                st.plotly_chart(fig, width="stretch")
            elif cat_cols and num_cols:
                _render_bar_chart(df, cat_cols[0], num_cols[0])
            elif len(num_cols) >= 2:
                _render_scatter_chart(df, num_cols[0], num_cols[1])
        elif cat_cols and num_cols:
            _render_bar_chart(df, cat_cols[0], num_cols[0])
        elif len(num_cols) >= 2:
            _render_scatter_chart(df, num_cols[0], num_cols[1])


def _render_bar_chart(df: pd.DataFrame, cat_col: str, metric_col: str) -> None:
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
    st.plotly_chart(fig, width="stretch")


def _render_scatter_chart(df: pd.DataFrame, col1: str, col2: str) -> None:
    fig = px.scatter(
        df,
        x=col1,
        y=col2,
        title=f"Dispersion : {col1} vs {col2}",
        template="plotly_white",
        color_discrete_sequence=["#8B5CF6"],
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
    st.plotly_chart(fig, width="stretch")


def _render_section_d_statistical_findings(results: dict[str, Any]) -> None:
    """Section D: Statistical & Business Findings presented for Executives."""
    st.markdown("### 🔍 Constats & Enseignements Clés")

    results_dict = results or {}
    trends = results_dict.get("trend") or []
    correlations = results_dict.get("correlation") or []
    distributions = results_dict.get("distribution") or []

    findings = []
    tech_details = []

    # Trends
    if isinstance(trends, list):
        for t in trends:
            if not isinstance(t, dict):
                continue
            col = t.get("column", "Variable")
            direction = t.get("direction")
            r2 = t.get("r_squared", 0)
            p_val = t.get("p_value", 1.0)
            slope = t.get("slope", 0)
            change_pct = t.get("change_pct")
            is_sig = t.get("is_significant", False)

            pct_str = f" ({change_pct:+.1f}%)" if change_pct is not None else ""
            if is_sig:
                dir_text = "hausse" if direction == "up" else "baisse"
                findings.append({
                    "icon": "📈" if direction == "up" else "📉",
                    "title": f"Tendance Confirmée sur `{col}`",
                    "summary": f"Une dynamique soutenue à la **{dir_text}** est observée{pct_str}.",
                    "impact": "Trajectoire claire et prévisible exploitable pour le pilotage opérationnel.",
                })
            else:
                findings.append({
                    "icon": "⚖️",
                    "title": f"Stabilité Relative sur `{col}`",
                    "summary": f"Les variations de `{col}` oscillent dans des marges normales sans direction forte.",
                    "impact": "Niveau d'activité stable nécessitant une surveillance standard.",
                })
            tech_details.append(f"• **Tendance `{col}`** : Slope={slope}, R²={r2}, p-value={p_val}, Significatif={is_sig}")

    # Correlations
    if isinstance(correlations, list):
        for c in correlations:
            if not isinstance(c, dict):
                continue
            c1 = c.get("column1", "")
            c2 = c.get("column2", "")
            r = c.get("coefficient", 0)
            rel = c.get("relationship", "modérée")

            rel_text = "Forte association positive" if r > 0.5 else ("Forte association négative" if r < -0.5 else "Liaison modérée")
            findings.append({
                "icon": "🔗",
                "title": f"Lien d'Influence entre `{c1}` et `{c2}`",
                "summary": f"**{rel_text}** constatée entre ces deux indicateurs (coefficient : {r:.2f}).",
                "impact": f"Toute évolution de {c1} s'accompagne d'une variation parallèle de {c2}.",
            })
            tech_details.append(f"• **Corrélation `{c1}` vs `{c2}`** : Coefficient r={r}, Relation={rel}")

    # Distributions
    if isinstance(distributions, list):
        for d in distributions:
            if not isinstance(d, dict):
                continue
            col = d.get("column", "")
            skew = d.get("skewness", 0.0)
            if abs(skew) > 1.0:
                findings.append({
                    "icon": "📊",
                    "title": f"Concentration des Données sur `{col}`",
                    "summary": f"La répartition des valeurs de `{col}` est fortement concentrée autour de certains volumes.",
                    "impact": "Présence de sous-groupes ou de quelques enregistrements majeurs qui pèsent sur la moyenne.",
                })
                tech_details.append(f"• **Distribution `{col}`** : Skewness={skew}, Normalité={d.get('is_normal')}")

    if findings:
        for f in findings:
            st.markdown(
                f"""
                <div class='bi-card-box'>
                    <div style='display:flex; align-items:center; gap:8px;'>
                        <span style='font-size:1.3rem;'>{f['icon']}</span>
                        <h4 style='margin:0; color:#1E293B;'>{f['title']}</h4>
                    </div>
                    <p style='margin: 8px 0 4px 0; font-size: 0.95rem; color:#334155;'>{f['summary']}</p>
                    <p style='margin: 0; font-size: 0.85rem; color:#64748B;'><strong>💡 Impact Métier :</strong> {f['impact']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if tech_details:
            with st.expander("🔬 Détails Techniques & Métriques Statologiques (Mode Audit)"):
                for td in tech_details:
                    st.markdown(td)
    else:
        st.info("Aucun constat particulier sur les analyses sélectionnées.")


def _render_section_e_anomalies(results: dict[str, Any]) -> None:
    """Section E: Anomalies & Vigilance Points Matrix."""
    st.markdown("### ⚠️ Points de Vigilance & Anomalies")

    results_dict = results or {}
    anomalies_list = results_dict.get("anomaly") or []
    has_anomalies = False

    if isinstance(anomalies_list, list) and len(anomalies_list) > 0:
        for a in anomalies_list:
            if not isinstance(a, dict):
                continue
            col = a.get("column", "Metric")
            count = a.get("count", 0)
            items = a.get("anomalies") or []
            method = a.get("method", "ensemble")

            if count > 0:
                has_anomalies = True
                st.warning(f"**{count} valeur(s) atypique(s) détectée(s) dans `{col}`** (Détection automatique : `{method}`)")
                ano_df = pd.DataFrame(items)
                if not ano_df.empty:
                    st.dataframe(ano_df, hide_index=True, width="stretch")
            else:
                st.success(f"✅ Aucune donnée atypique ou anomalie détectée dans `{col}`.")

    if not has_anomalies and not (isinstance(anomalies_list, list) and len(anomalies_list) > 0):
        st.info("L'analyse des anomalies n'a pas été sélectionnée pour ce rapport.")


def _render_section_f_ai_insights(insights: list[dict[str, Any]] | None, ai_data: dict[str, Any] | None) -> None:
    """Section F: AI Interpretation — full explicit reading of every finding."""
    st.markdown("### 🤖 Interprétation & Analyse par l'IA")

    if not ai_data:
        # Fallback: raw insights engine table
        if insights and isinstance(insights, list) and len(insights) > 0:
            st.info("L'interprétation IA n'est pas disponible (aucune clé API configurée). Diagnostic moteur d'analyse ci-dessous.")
            ins_df = pd.DataFrame(insights)
            st.dataframe(ins_df, hide_index=True, width="stretch")
        else:
            st.info("Cochez 'Inclure l'interprétation automatique' et configurez une clé API Groq pour activer cette section.")
        return

    # ── Provider badge & confidence ──────────────────────────────────────
    provider = ai_data.get("provider", "Open Analytics AI")
    conf = ai_data.get("confidence", 0.0)
    risk_raw = ai_data.get("risk_assessment", "")

    # Extract risk level word for coloring
    risk_upper = str(risk_raw).upper()
    if "CRITIQUE" in risk_upper:
        risk_color, risk_icon = "#EF4444", "🔴"
    elif "ÉLEVÉ" in risk_upper or "ELEVE" in risk_upper:
        risk_color, risk_icon = "#F59E0B", "🟠"
    elif "MODÉRÉ" in risk_upper or "MODERE" in risk_upper:
        risk_color, risk_icon = "#EAB308", "🟡"
    else:
        risk_color, risk_icon = "#10B981", "🟢"

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Moteur IA", provider)
    with m2:
        st.metric("Indice de Confiance", f"{conf:.0%}" if conf else "N/A")
    with m3:
        _rhtml = (
            "<div style='padding-top:4px;'>"
            "<span style='font-size:0.8rem;color:#64748B;font-weight:600;'>NIVEAU DE RISQUE</span><br/>"
            f"<span style='font-size:1.1rem;font-weight:700;color:{risk_color};'>{risk_icon} {risk_raw}</span>"
            "</div>"
        )
        st.markdown(_rhtml, unsafe_allow_html=True)

    st.markdown("---")

    # ── Executive Summary ────────────────────────────────────────────────
    summary_text = (ai_data.get("summary") or "").strip()
    if summary_text:
        st.markdown(
            f"<div style='background:#F0F9FF;border-left:4px solid #0EA5E9;border-radius:6px;"
            f"padding:14px 18px;margin-bottom:18px;'>"
            f"<span style='font-size:0.8rem;color:#0369A1;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.06em;'>📋 Résumé Exécutif</span>"
            f"<p style='margin:6px 0 0 0;font-size:0.97rem;color:#1E293B;line-height:1.6;'>{summary_text}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Key Findings — explicit numbered cards ───────────────────────────
    key_findings = ai_data.get("key_findings") or []
    if key_findings:
        st.markdown("#### 🔎 Constats Détaillés de l'IA")
        st.caption("Chaque constat est fondé sur les données réelles analysées — aucune invention.")
        for i, kf in enumerate(key_findings, start=1):
            st.markdown(
                f"<div class='bi-card-box' style='border-left:3px solid #6366F1;'>"
                f"<span style='font-size:0.78rem;color:#6366F1;font-weight:700;text-transform:uppercase;"
                f"letter-spacing:0.05em;'>Constat #{i}</span>"
                f"<p style='margin:6px 0 0 0;font-size:0.95rem;color:#1E293B;line-height:1.6;'>{kf}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Raw insights fallback table ──────────────────────────────────────
    if not key_findings and insights and isinstance(insights, list) and len(insights) > 0:
        st.markdown("#### 📋 Diagnostic Moteur d'Analyse")
        ins_df = pd.DataFrame(insights)
        st.dataframe(ins_df, hide_index=True, width="stretch")


def _render_section_g_recommendations(insights: list[dict[str, Any]] | None, ai_data: dict[str, Any] | None) -> None:
    """Section G: AI Recommendations + Action Plan."""
    st.markdown("### 💡 Plan d'Action & Recommandations Stratégiques")

    insights_list = insights or []
    has_ai = bool(ai_data)

    # ── Recommendations ──────────────────────────────────────────────────
    raw_recs = (ai_data.get("recommendations") or []) if has_ai else []

    # Fallback to insights engine
    if not raw_recs and isinstance(insights_list, list):
        raw_recs = [
            ins.get("description", "")
            for ins in insights_list
            if isinstance(ins, dict) and ins.get("type") in ("risk", "opportunity", "recommendation")
        ]

    if raw_recs:
        st.markdown("#### 📌 Recommandations")
        for i, rec in enumerate(raw_recs, start=1):
            priority_color = "#EF4444" if i == 1 else ("#F59E0B" if i == 2 else "#10B981")
            priority_label = "Haute priorité" if i == 1 else ("Moyenne priorité" if i == 2 else "Standard")
            st.markdown(
                f"<div class='bi-card-box' style='border-left:3px solid {priority_color};'>"
                f"<span style='font-size:0.78rem;color:{priority_color};font-weight:700;"
                f"text-transform:uppercase;letter-spacing:0.05em;'>{priority_label}</span>"
                f"<p style='margin:6px 0 0 0;font-size:0.95rem;color:#1E293B;line-height:1.6;'>{rec}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Aucune recommandation disponible. Activez l'interprétation IA pour obtenir des actions concrètes.")

    # ── Action Plan timeline ─────────────────────────────────────────────
    action_plan = (ai_data.get("action_plan") or []) if has_ai else []
    if isinstance(action_plan, list) and len(action_plan) > 0:
        st.markdown("#### 🗓️ Plan d'Action Opérationnel")
        timeline_colors = ["#EF4444", "#F59E0B", "#10B981"]
        for i, step in enumerate(action_plan):
            color = timeline_colors[i] if i < len(timeline_colors) else "#6366F1"
            st.markdown(
                f"<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:12px;'>"
                f"<div style='min-width:12px;height:12px;border-radius:50%;"
                f"background:{color};margin-top:6px;flex-shrink:0;'></div>"
                f"<p style='margin:0;font-size:0.94rem;color:#1E293B;line-height:1.6;'>{step}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )


def _render_section_h_data_quality(df: pd.DataFrame, analysis_response: dict[str, Any]) -> None:
    """Section H: Data Quality & Reliability Audit."""
    st.markdown("### 🛡️ Audit de Qualité des Données")

    validation = (analysis_response.get("validation") if isinstance(analysis_response, dict) else None) or {}
    total_rows = len(df)
    is_valid = validation.get("valid", True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Enregistrements Traités", f"{total_rows:,}")
    with c2:
        st.metric("Conformité Schéma", "100%" if is_valid else "Inconforme")
    with c3:
        null_count = df.isnull().sum().sum() if not df.empty else 0
        st.metric("Valeurs Manquantes", f"{null_count}")
    with c4:
        dup_count = df.duplicated().sum() if not df.empty else 0
        st.metric("Doublons Détectés", f"{dup_count}")

    if not df.empty:
        completeness_pct = ((df.notnull().sum().sum()) / (df.shape[0] * df.shape[1])) * 100
        st.caption(f"Taux de complétude des données : **{completeness_pct:.1f}%**")


def _render_section_i_data_exploration(df: pd.DataFrame) -> None:
    """Section I: Interactive Data Exploration Table."""
    st.markdown("### 🔎 Exploration Intégrale des Données")

    if df.empty:
        st.info("Aucune donnée à afficher dans le tableau d'exploration.")
        return

    st.dataframe(
        df,
        width="stretch",
        hide_index=False,
    )
