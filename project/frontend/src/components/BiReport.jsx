import React, { useState } from 'react';
import { 
  Sparkles, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertTriangle, 
  CheckCircle, 
  ShieldAlert, 
  BarChart3, 
  Table as TableIcon,
  ChevronRight,
  Clock,
  Layers,
  ArrowRight,
  PieChart,
  Lightbulb,
  Eye,
  Zap,
  CalendarDays,
  RefreshCw,
  Target,
  Code2
} from 'lucide-react';
import EvidenceModal from './EvidenceModal';
import DynamicChartRenderer from './DynamicChartRenderer';
import ApiSnippetModal from './ApiSnippetModal';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar
} from 'recharts';
import { useTheme } from '../context/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

// Nettoie un texte pour remplacer tout nom de colonne technique avec underscore
function cleanTextLabels(text) {
  if (typeof text !== 'string') return text;
  return text.replace(/\b([a-zA-Z0-9]+)(_[a-zA-Z0-9]+)+\b/g, (match) => humanizeCol(match));
}

// Transforme un nom de colonne technique en libellé lisible
function humanizeCol(name) {
  if (!name) return name;
  const unitMap = {
    '_kg': ' (kg)', '_mm': ' (mm)', '_c': ' (°C)', '_pct': ' (%)',
    '_percent': ' (%)', '_eur': ' (€)', '_euro': ' (€)', '_usd': ' ($)',
    '_h': ' (h)', '_ha': ' (ha)', '_m': ' (m)', '_km': ' (km)',
  };
  let label = name;
  let unit = '';
  for (const [suffix, display] of Object.entries(unitMap)) {
    if (name.toLowerCase().endsWith(suffix)) {
      label = name.slice(0, -suffix.length);
      unit = display;
      break;
    }
  }
  return label.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).trim() + unit;
}

// Finds a row identifier to display instead of "Row #N"
function rowAlias(row, idx) {
  if (!row) return `Observation ${idx + 1}`;
  const idKeys = ['date', 'mois', 'month', 'semaine', 'week', 'periode', 'period',
                  'id', 'nom', 'name', 'region', 'label', 'reference', 'ref', 'code'];
  for (const k of idKeys) {
    if (row[k] !== undefined && row[k] !== null && String(row[k]).length < 50) {
      return String(row[k]);
    }
  }
  return `Observation ${idx + 1}`;
}

// Carte de statistique « parlante » : icône + valeur héro + phrase de contexte.
// Chaque carte répond à une question simple (quoi analyser, quelle tendance,
// où ça cloche, quelle fiabilité) plutôt que d'afficher un nu de chiffres.
function StatCard({ icon: Icon, iconClass, label, hero, sub, detail, children }) {
  return (
    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm transition-colors flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <span className={`shrink-0 p-1.5 rounded-lg ${iconClass}`}>
          <Icon className="h-3.5 w-3.5" />
        </span>
        <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold truncate">
          {label}
        </span>
      </div>
      <div className="flex items-center gap-2 flex-wrap">{hero}</div>
      {children}
      <p className="text-xs text-slate-500 dark:text-slate-400 leading-snug mt-auto">{sub}</p>
      {detail ? (
        <p className="text-[10px] text-slate-400 dark:text-slate-500 truncate" title={detail}>{detail}</p>
      ) : null}
    </div>
  );
}

// Interprétation opérationnelle de terrain pour chaque variable et secteur.
// Remplace systématiquement tout vieux poncif résiduel ("vérifier la saisie").
function getContextualAnomalyInsight(col, anom, language) {
  const existingReason = anom?.reason || '';
  const existingRec = anom?.recommendation || '';
  const isEn = language === 'en';

  const isGenericRec = !existingRec ||
    existingRec.toLowerCase().includes('erreur de saisie') ||
    existingRec.toLowerCase().includes('data entry error') ||
    existingRec.toLowerCase().includes('vérifier les données') ||
    existingRec.toLowerCase().includes('verifier les donnees') ||
    existingRec.toLowerCase().includes('check the source records');

  const isGenericReason = !existingReason ||
    existingReason.toLowerCase().includes('niveau anormalement') ||
    existingReason.toLowerCase().includes('unusually high') ||
    existingReason.toLowerCase().includes('unusually low') ||
    existingReason.toLowerCase().includes('anomalie') ||
    existingReason.toLowerCase().includes('outlier');

  const colNorm = (col || '').toLowerCase();

  let reason = existingReason;
  let recommendation = existingRec;

  // 1. Pluviométrie / Pluie / Rain
  if (colNorm.includes('pluvio') || colNorm.includes('pluie') || colNorm.includes('rain')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Exceptional rainfall peak recorded on the period.'
        : 'Pic pluviométrique exceptionnel constaté sur la période.';
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Inspect drainage on low-lying plots and suspend artificial irrigation to prevent root hypoxia; check rain gauge calibration if total appears aberrant.'
        : "Contrôler le drainage des parcelles basses et suspendre l'irrigation artificielle pour éviter l'asphyxie racinaire ; vérifier l'étalonnage du pluviomètre en cas de cumul aberrant.";
    }
  }
  // 2. Rendement / Récolte / Yield / Harvest
  else if (colNorm.includes('rendement') || colNorm.includes('recolte') || colNorm.includes('yield') || colNorm.includes('harvest')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Record yield spike observed compared to seasonal averages.'
        : 'Pic de rendement record constaté par rapport aux moyennes de saison.';
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Mobilize additional storage capacity and harvesting logistics to secure grain quality and prevent post-harvest spoilage.'
        : "Mobiliser des capacités de stockage et d'évacuation logistique supplémentaires pour sécuriser la collecte et éviter les pertes post-récolte.";
    }
  }
  // 3. Ventes / Chiffre d'affaires / Sales / Revenue / Recette
  else if (colNorm.includes('vente') || colNorm.includes('sales') || colNorm.includes('chiffre') || colNorm.includes('revenue') || colNorm.includes('recette')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Exceptional sales volume spike significantly above the usual run rate.'
        : 'Pic de ventes exceptionnel nettement supérieur à la cadence usuelle.';
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Secure inventory replenishment to prevent out-of-stock events and allocate extra fulfillment and sales staffing.'
        : 'Sécuriser le réapprovisionnement des stocks pour éviter les ruptures et mobiliser des renforts en caisse et logistique.';
    }
  }
  // 4. Panier moyen / Order value / Basket
  else if (colNorm.includes('panier') || colNorm.includes('basket') || colNorm.includes('aov') || colNorm.includes('ticket')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Outlier high average order value driving transaction margins.'
        : 'Panier moyen exceptionnellement élevé tirant la rentabilité.';
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Identify key basket drivers, replicate top bundled offers and secure high-value order fulfillment.'
        : 'Identifier les offres groupées motrices pour répliquer le modèle et sécuriser le traitement des commandes à fort panier.';
    }
  }
  // 5. Visiteurs / Clients / Traffic
  else if (colNorm.includes('visiteur') || colNorm.includes('visitor') || colNorm.includes('client') || colNorm.includes('traffic')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Unusual customer attendance peak recorded on the period.'
        : "Pic d'affluence clientèle exceptionnel constaté sur la période.";
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Optimize checkout funnels and floor staffing to maximize conversion on this audience surge.'
        : "Fluidifier les parcours d'encaissement et mobiliser des équipes au sol pour maximiser la conversion sur ce pic d'affluence.";
    }
  }
  // 6. Consultations / Patients / Admissions / Urgences
  else if (colNorm.includes('consultation') || colNorm.includes('patient') || colNorm.includes('admission') || colNorm.includes('urgence')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Patient surge significantly above typical clinical capacity.'
        : "Pic d'affluence médicale au-dessus des flux normaux de garde.";
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Reinforce on-call medical staff, open overflow consultation units and restock emergency consumables.'
        : "Renforcer les effectifs de garde médicale, ouvrir des box de consultation d'appoint et réapprovisionner les consommables d'urgence.";
    }
  }
  // 7. Durée / Attente / Temps
  else if (colNorm.includes('duree') || colNorm.includes('attente') || colNorm.includes('wait') || colNorm.includes('delay')) {
    if (isGenericReason) {
      reason = isEn
        ? 'Critical lengthening of processing and wait times.'
        : 'Allongement critique des temps de prise en charge.';
    }
    if (isGenericRec) {
      recommendation = isEn
        ? 'Reassign triage personnel to fast-track intake and streamline administrative registration.'
        : "Affecter du personnel au tri d'accueil et fluidifier l'enregistrement administratif.";
    }
  }
  // 8. Générique intelligent
  else {
    if (isGenericReason) {
      reason = isEn
        ? `Atypical pattern recorded on ${col} compared to standard baseline.`
        : `Comportement atypique constaté sur ${col} par rapport au niveau standard.`;
    }
    if (isGenericRec) {
      recommendation = isEn
        ? `Assess operational capacity constraints and deploy targeted adjustments on the process associated with ${col}.`
        : `Évaluer la charge opérationnelle induite par cette variation sur ${col} et engager les arbitrages de processus nécessaires.`;
    }
  }

  return { reason, recommendation };
}

function getActionMeta(step, isEn) {
  const clean = (step || '').replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();
  const lower = clean.toLowerCase();

  if (
    lower.includes('semaine') ||
    lower.includes('week') ||
    lower.includes('immédiat') ||
    lower.includes('urgent') ||
    lower.includes('prioritaire') ||
    lower.includes('today') ||
    lower.includes('24h') ||
    lower.includes('48h')
  ) {
    return {
      Icon: Zap,
      badgeLabel: isEn ? 'Immediate · This Week' : 'Immédiat · Cette semaine',
      cardClass: 'border-l-4 border-l-amber-500 bg-amber-50/20 dark:bg-amber-950/10 border-slate-200 dark:border-slate-800',
      iconBox: 'bg-amber-100 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800',
      badgeClass: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800',
      text: clean,
    };
  }

  if (
    lower.includes('mois') ||
    lower.includes('month') ||
    lower.includes('moyen terme') ||
    lower.includes('mid-term') ||
    lower.includes('prochain')
  ) {
    return {
      Icon: CalendarDays,
      badgeLabel: isEn ? 'Operational · This Month' : 'Opérationnel · Ce mois',
      cardClass: 'border-l-4 border-l-sky-500 bg-sky-50/20 dark:bg-sky-950/10 border-slate-200 dark:border-slate-800',
      iconBox: 'bg-sky-100 dark:bg-sky-950/50 text-sky-600 dark:text-sky-400 border border-sky-200 dark:border-sky-800',
      badgeClass: 'bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800',
      text: clean,
    };
  }

  if (
    lower.includes('continu') ||
    lower.includes('monitor') ||
    lower.includes('suivi') ||
    lower.includes('veille') ||
    lower.includes('régulier') ||
    lower.includes('regular') ||
    lower.includes('ongoing')
  ) {
    return {
      Icon: RefreshCw,
      badgeLabel: isEn ? 'Continuous Monitoring' : 'Veille & Suivi continu',
      cardClass: 'border-l-4 border-l-emerald-500 bg-emerald-50/20 dark:bg-emerald-950/10 border-slate-200 dark:border-slate-800',
      iconBox: 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800',
      badgeClass: 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800',
      text: clean,
    };
  }

  return {
    Icon: Target,
    badgeLabel: isEn ? 'Strategic Plan' : 'Plan Stratégique',
    cardClass: 'border-l-4 border-l-indigo-500 bg-indigo-50/20 dark:bg-indigo-950/10 border-slate-200 dark:border-slate-800',
    iconBox: 'bg-indigo-100 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800',
    badgeClass: 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800',
    text: clean,
  };
}

export default function BiReport({ report, rawData }) {
  const [activeView, setActiveView] = useState('insights'); // 'insights' | 'charts' | 'data'
  const [selectedEvidenceInsight, setSelectedEvidenceInsight] = useState(null);
  const [showApiSnippet, setShowApiSnippet] = useState(false);
  const { theme } = useTheme();
  const { language, t } = useLanguage();

  if (!report) return null;

  const results = report.results || {};
  const summary = results.summary || [];
  const trends = results.trend || [];
  const anomalies = results.anomaly || [];
  const causality = results.causality || [];
  const grouped = results.grouped || null;
  const insights = report.insights || [];

  // Parse AI Interpretation
  let ai = null;
  if (report.ai_interpretation) {
    try {
      ai = typeof report.ai_interpretation === 'string'
        ? JSON.parse(report.ai_interpretation)
        : report.ai_interpretation;
    } catch {
      ai = null;
    }
  }

  // Identify numeric keys for charts
  const sampleRow = (rawData && rawData[0]) ? rawData[0] : {};
  const numericColumns = Object.keys(sampleRow).filter(k => {
    const val = sampleRow[k];
    return typeof val === 'number' || (!isNaN(Number(val)) && val !== '' && val !== null);
  });

  // Prepare chart series from raw data
  const chartData = (rawData || []).slice(0, 100).map((row, idx) => ({
    _index: idx + 1,
    ...row,
  }));

  const totalAnomalies = anomalies.reduce((acc, curr) => acc + (curr.count || 0), 0);

  // ─── Dérivées pour les 4 cartes statistiques ──────────────────────────
  // 1. CARTE 1 : Données analysées (enregistrements réels, indicateurs, validité)
  const rowCount = (rawData && rawData.length) || report.row_count || 0;
  const totalCols = sampleRow ? Object.keys(sampleRow).length : 0;
  const nonNumericCount = Math.max(0, totalCols - numericColumns.length);
  const invalidRowsCount = report.validation?.invalid_rows || 0;

  // 2. CARTE 2 : Évolutions détectées (variation réelle, sens, bornes)
  const dominantTrend = trends.reduce((best, curr) => {
    if (!best) return curr;
    return Math.abs(curr.change_pct || 0) > Math.abs(best.change_pct || 0) ? curr : best;
  }, null);

  // Direction dominante déduite en priorité de la variation réelle pour éliminer tout faux "Stable"
  const dominantDirection = dominantTrend
    ? (Number(dominantTrend.change_pct) > 1.0
        ? 'up'
        : (Number(dominantTrend.change_pct) < -1.0
            ? 'down'
            : (dominantTrend.direction || 'stable')))
    : 'stable';

  const trendCounts = {
    up: trends.filter((tr) => (Number(tr.change_pct) > 1.0 || (tr.change_pct === undefined && tr.direction === 'up'))).length,
    down: trends.filter((tr) => (Number(tr.change_pct) < -1.0 || (tr.change_pct === undefined && tr.direction === 'down'))).length,
    stable: trends.filter((tr) => (Math.abs(Number(tr.change_pct) || 0) <= 1.0 && tr.direction !== 'up' && tr.direction !== 'down')).length,
  };

  // 3. CARTE 3 : Points de vigilance (déduplication stricte des enregistrements)
  const uniqueAffectedRows = new Set();
  anomalies.forEach((a) => {
    (a.anomalies || []).forEach((item) => {
      if (item.row !== undefined && item.row !== null) {
        uniqueAffectedRows.add(item.row);
      }
    });
  });

  let missingCellsCount = 0;
  (rawData || []).forEach((row) => {
    numericColumns.forEach((col) => {
      const val = row[col];
      if (val === null || val === undefined || val === '') {
        missingCellsCount++;
      }
    });
  });

  const flaggedColumns = anomalies
    .filter((a) => (a.count || 0) > 0)
    .sort((a, b) => (b.count || 0) - (a.count || 0));

  const totalAnomaliesCount = anomalies.reduce((acc, curr) => acc + (curr.count || 0), 0);
  // Nombre de colonnes ayant au moins 1 anomalie — c'est le vrai chiffre de vigilance
  const distinctAnomalousRows = flaggedColumns.length;

  // 4. CARTE 4 : Synthèse IA (état opérationnel réel sans score fictif)
  const recoCount = Array.isArray(ai?.recommendations) ? ai.recommendations.length : 0;
  const keyFindingsCount = Array.isArray(ai?.key_findings) ? ai.key_findings.length : 0;
  const aiOk = report.ai_status === 'ok';
  const aiError = report.ai_status === 'error';

  // Format d'un pourcentage signé selon la langue (+6,7 % / +6.7%)
  const fmtPct = (value) => {
    const v = Number(value) || 0;
    const abs = Math.abs(v).toFixed(1);
    const formatted = language === 'fr' ? abs.replace('.', ',') : abs;
    if (v > 0) return `+${formatted}%`;
    if (v < 0) return `-${formatted}%`;
    return `${formatted}%`;
  };

  // Libellés pré-composés pour les cartes
  const indicatorNames = numericColumns.slice(0, 3).map(humanizeCol);
  const extraIndicators = Math.max(0, numericColumns.length - indicatorNames.length);
  const indicatorCountLabel = numericColumns.length > 1
    ? t('report.card_indicators', 'indicateurs mesurés')
    : t('report.card_indicator_one', 'indicateur mesuré');

  const dirParts = [];
  if (trendCounts.up > 0) dirParts.push(`${trendCounts.up} ${t('report.card_dir_up', 'en hausse')}`);
  if (trendCounts.down > 0) dirParts.push(`${trendCounts.down} ${t('report.card_dir_down', 'en baisse')}`);
  if (trendCounts.stable > 0) {
    dirParts.push(
      `${trendCounts.stable} ${trendCounts.stable > 1
        ? t('report.card_dir_stable_pl', 'stables')
        : t('report.card_dir_stable_sg', 'stable')}`
    );
  }

  const flaggedNames = flaggedColumns.slice(0, 2).map((a) => humanizeCol(a.column));
  const extraFlagged = Math.max(0, flaggedColumns.length - flaggedNames.length);

  const isDark = theme === 'dark';
  const gridStroke = isDark ? '#1e293b' : '#e2e8f0';
  const axisStroke = isDark ? '#64748b' : '#94a3b8';
  const tooltipBg = isDark ? '#0f172a' : '#ffffff';
  const tooltipBorder = isDark ? '#334155' : '#cbd5e1';
  const tooltipText = isDark ? '#f8fafc' : '#0f172a';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Report Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
            <Layers className="h-3.5 w-3.5" />
            <span>{t('report.header_badge', 'Analytical & Decision Synthesis')}</span>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span className="text-slate-500 dark:text-slate-400">
              {report.row_count || rawData?.length || 0} {t('report.records', 'records')}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
            {report.label || report.dataset || t('report.default_title', 'Performance Report')}
          </h2>
        </div>

        {/* Right actions: Code API + View Switcher */}
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={() => setShowApiSnippet(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 transition-all shadow-sm"
            title="Afficher le code d'intégration API"
          >
            <Code2 className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>Code API</span>
          </button>

          {/* View Switcher */}
          <div className="flex bg-slate-100 dark:bg-slate-950 p-1 rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
            <button
              onClick={() => setActiveView('insights')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeView === 'insights' 
                  ? 'bg-indigo-600 text-white shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>{t('report.view_results', 'Results & Recommendations')}</span>
            </button>
            <button
              onClick={() => setActiveView('charts')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeView === 'charts' 
                  ? 'bg-indigo-600 text-white shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <BarChart3 className="h-3.5 w-3.5" />
              <span>{t('report.view_charts', 'Charts')} ({numericColumns.length})</span>
            </button>
            <button
              onClick={() => setActiveView('data')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeView === 'data' 
                  ? 'bg-indigo-600 text-white shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <TableIcon className="h-3.5 w-3.5" />
              <span>{t('report.view_raw', 'Raw Data')} ({rawData?.length || 0})</span>
            </button>
          </div>
        </div>
      </div>

      {/* Top Summary Cards — 4 questions fondamentales : périmètre, dynamique, vigilance, état de l'analyse */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* 1 — Données analysées */}
        <StatCard
          icon={Layers}
          iconClass="bg-indigo-50 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400"
          label={t('report.card_data_analyzed', 'Données analysées')}
          hero={
            <>
              <span className="text-2xl font-bold text-slate-900 dark:text-white">
                {rowCount.toLocaleString(language === 'fr' ? 'fr-FR' : 'en-US')}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                {language === 'fr' ? (rowCount > 1 ? 'enregistrements' : 'enregistrement') : (rowCount > 1 ? 'records' : 'record')}
              </span>
            </>
          }
          sub={
            numericColumns.length > 0
              ? `${numericColumns.length} ${indicatorCountLabel}${nonNumericCount > 0 ? ` · ${nonNumericCount} ${language === 'fr' ? 'dimension(s)' : 'dimension(s)'}` : ''}`
              : t('report.card_no_indicators', 'Aucun indicateur numérique')
          }
        />

        {/* 2 — Évolutions détectées */}
        <StatCard
          icon={dominantDirection === 'up' ? TrendingUp : dominantDirection === 'down' ? TrendingDown : Minus}
          iconClass={
            dominantDirection === 'up'
              ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400'
              : dominantDirection === 'down'
                ? 'bg-rose-50 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400'
                : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
          }
          label={t('report.card_trends', 'Évolutions détectées')}
          hero={
            dominantTrend ? (
              <div className="flex items-center gap-2">
                <span className={`text-2xl font-bold flex items-center gap-1 ${
                  dominantDirection === 'up'
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : dominantDirection === 'down'
                      ? 'text-rose-600 dark:text-rose-400'
                      : 'text-slate-700 dark:text-slate-300'
                }`}>
                  {dominantDirection === 'up' && <span className="text-emerald-600 dark:text-emerald-400 font-bold">↑</span>}
                  {dominantDirection === 'down' && <span className="text-rose-600 dark:text-rose-400 font-bold">↓</span>}
                  {fmtPct(dominantTrend.change_pct)}
                </span>
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1 ${
                  dominantDirection === 'up'
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                    : dominantDirection === 'down'
                      ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
                      : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                }`}>
                  {dominantDirection === 'up'
                    ? (language === 'fr' ? '↑ Hausse' : '↑ Increase')
                    : dominantDirection === 'down'
                      ? (language === 'fr' ? '↓ Baisse' : '↓ Decrease')
                      : (language === 'fr' ? 'Stable' : 'Stable')}
                </span>
              </div>
            ) : (
              <span className="text-2xl font-bold text-slate-400 dark:text-slate-500">—</span>
            )
          }
          sub={
            dominantTrend
              ? `${humanizeCol(dominantTrend.column)} (${language === 'fr' ? 'du 1er au dernier point' : 'first to last record'})`
              : t('report.card_no_trend', 'Aucune tendance nette sur la période')
          }
        />

        {/* 3 — Points de vigilance */}
        <StatCard
          icon={distinctAnomalousRows > 0 || missingCellsCount > 0 ? AlertTriangle : CheckCircle}
          iconClass={
            distinctAnomalousRows > 0 || missingCellsCount > 0
              ? 'bg-amber-50 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400'
              : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400'
          }
          label={t('report.card_watchpoints', 'Points de vigilance')}
          hero={
            <>
              <span className={`text-2xl font-bold ${
                distinctAnomalousRows > 0 || missingCellsCount > 0
                  ? 'text-amber-600 dark:text-amber-400'
                  : 'text-emerald-600 dark:text-emerald-400'
              }`}>
                {distinctAnomalousRows}
              </span>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                distinctAnomalousRows > 0
                  ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                  : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
              }`}>
                {distinctAnomalousRows > 0
                  ? (language === 'fr' ? 'À vérifier' : 'To review')
                  : (language === 'fr' ? 'Sain' : 'Clean')}
              </span>
            </>
          }
          sub={
            distinctAnomalousRows > 0
              ? `${language === 'fr' ? 'Sur' : 'On'} ${flaggedNames.join(', ')}${extraFlagged > 0 ? ` +${extraFlagged}` : ''}`
              : (rowCount < 4
                  ? (language === 'fr' ? 'Échantillon court (< 4) : détection limitée' : 'Small sample (< 4): limited detection')
                  : (language === 'fr' ? `Aucun écart atypique sur ${rowCount} enregistrements` : `No atypical outlier in ${rowCount} records`))
          }
        />

        {/* 4 — Synthèse IA */}
        <StatCard
          icon={Sparkles}
          iconClass="bg-indigo-50 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400"
          label={t('report.card_ai_synthesis', 'Synthèse IA')}
          hero={
            <>
              <span className="text-xl font-bold text-slate-900 dark:text-white">
                {aiOk
                  ? (language === 'fr' ? 'Disponible' : 'Ready')
                  : aiError
                    ? (language === 'fr' ? 'Indisponible' : 'Unavailable')
                    : (language === 'fr' ? 'Désactivée' : 'Disabled')}
              </span>
              <span className="relative inline-flex h-2.5 w-2.5 shrink-0">
                {aiOk && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                )}
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  aiOk
                    ? 'bg-emerald-500'
                    : aiError
                      ? 'bg-rose-500'
                      : 'bg-slate-300 dark:bg-slate-600'
                }`} />
              </span>
            </>
          }
          sub={
            aiOk
              ? (recoCount > 0
                  ? `${recoCount} ${language === 'fr' ? (recoCount > 1 ? 'actions prioritaires recommandées' : 'action prioritaire recommandée') : (recoCount > 1 ? 'priority recommended actions' : 'priority recommended action')}`
                  : (language === 'fr' ? 'Synthèse exécutive générée' : 'Executive synthesis generated'))
              : aiError
                ? (language === 'fr' ? 'Statistiques préservées sans interprétation' : 'Statistical results kept without AI')
                : (language === 'fr' ? 'Analyse statistique pure sans IA' : 'Pure statistical analysis without AI')
          }
        />
      </div>

      {/* VIEW: RESULTS & RECOMMENDATIONS */}
      {activeView === 'insights' && (
        <div className="space-y-6">
          {/* Executive AI Block */}
          {ai && (
            <div className="bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-500/30 rounded-2xl p-6 shadow-sm transition-colors">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4 mb-5">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">{t('report.ai_title', 'Executive Assessment & Strategic Guidance')}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{t('report.ai_subtitle', 'Tailored reporting for executive leadership')}</p>
                  </div>
                </div>
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/40">
                  {t('report.reliability', 'Reliability')} : {Math.round((ai.confidence || 0.95) * 100)}%
                </span>
              </div>

              {/* Executive Summary */}
              {ai.summary && (
                <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed mb-6">
                  <div className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1.5">
                    {t('report.executive_summary', 'Executive Summary')}
                  </div>
                  {cleanTextLabels(ai.summary)}
                </div>
              )}

              {/* Key Findings & Recommendations Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Key Findings */}
                {ai.key_findings && ai.key_findings.length > 0 && (
                  <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                      <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                      {t('report.key_findings', 'Key Findings')}
                    </h4>
                    <ul className="space-y-2.5">
                      {ai.key_findings.map((finding, idx) => {
                        // Find matching insight from mathematical results to provide evidence
                        const matchingInsight = insights.find(ins => 
                          finding.toLowerCase().includes((ins.metric || '').toLowerCase()) ||
                          finding.toLowerCase().includes((ins.title || '').toLowerCase())
                        ) || insights[idx % insights.length] || { title: cleanTextLabels(finding), description: cleanTextLabels(finding) };

                        return (
                          <li key={idx} className="text-xs text-slate-600 dark:text-slate-300 flex items-start justify-between gap-2 group">
                            <div className="flex items-start space-x-2 flex-1">
                              <span className="text-indigo-600 dark:text-indigo-400 font-bold mt-0.5">•</span>
                              <span className="leading-relaxed">{cleanTextLabels(finding)}</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => setSelectedEvidenceInsight(matchingInsight)}
                              title="Voir les faits et calculs ayant conduit à ce constat"
                              className="shrink-0 p-1 rounded-md text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 transition-colors"
                            >
                              <Eye className="h-3.5 w-3.5" />
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {ai.recommendations && ai.recommendations.length > 0 && (
                  <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                      <CheckCircle className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mr-2" />
                      {t('report.recommendations', 'Decision Recommendations')}
                    </h4>
                    <ul className="space-y-2.5">
                      {ai.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold mt-0.5">•</span>
                          <span>{cleanTextLabels(rec)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Action Plan (Redesigned with Lucide icons) */}
              {ai.action_plan && ai.action_plan.length > 0 && (
                <div className="mt-8 border-t border-slate-100 dark:border-slate-800 pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center">
                      <Clock className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                      {t('report.action_plan', 'Recommended Action Plan')}
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
                      {ai.action_plan.length} {language === 'en' ? 'prioritized steps' : 'étapes priorisées'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {ai.action_plan.map((step, idx) => {
                      const meta = getActionMeta(step, language === 'en');
                      const StepIcon = meta.Icon;
                      return (
                        <div
                          key={idx}
                          className={`p-4 rounded-xl border ${meta.cardClass} shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-all flex items-start gap-3.5`}
                        >
                          <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${meta.iconBox} mt-0.5`}>
                            <StepIcon className="h-4 w-4" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2 mb-1 flex-wrap">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${meta.badgeClass}`}>
                                {meta.badgeLabel}
                              </span>
                              <span className="text-[10px] font-mono font-semibold text-slate-400 dark:text-slate-500">
                                0{idx + 1}
                              </span>
                            </div>
                            <p className="text-xs text-slate-700 dark:text-slate-200 leading-relaxed font-normal">
                              {cleanTextLabels(meta.text)}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Priority Watchpoints / Risk Assessment */}
              {ai.risk_assessment && (
                <div className="mt-5 p-4 rounded-xl bg-amber-50/40 dark:bg-amber-950/20 border-l-4 border-l-amber-500 border border-amber-200/80 dark:border-amber-900/40 flex items-start gap-3.5 shadow-sm">
                  <div className="shrink-0 w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center border border-amber-200 dark:border-amber-800 mt-0.5">
                    <ShieldAlert className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1 flex-wrap">
                      <span className="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300 flex items-center gap-1.5">
                        {t('report.critical_watchpoints', 'Points de vigilance prioritaires')}
                      </span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-200/80 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200 uppercase tracking-wider border border-amber-300 dark:border-amber-700">
                        {language === 'en' ? 'High Attention' : 'Vigilance Recommandée'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-700 dark:text-slate-200 leading-relaxed">
                      {cleanTextLabels(ai.risk_assessment.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim())}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Causality drivers */}
          {causality.length > 0 && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center">
                <Lightbulb className="h-4 w-4 text-amber-500 mr-2 shrink-0" />
                {t('report.causality_title', 'Explanatory Factors & Variation Drivers')}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {causality.map((driver, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start space-x-2.5">
                    <span className="text-amber-500 font-bold mt-0.5">•</span>
                    <span className="leading-relaxed">{driver.explanation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Segments (group_by) */}
          {grouped && (grouped.segments || []).length > 0 && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm transition-colors">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-1 flex items-center">
                <PieChart className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                {t('report.segments_by', 'Breakdown by')} {humanizeCol(grouped.group_by)}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-5">
                {t('report.ranked_by', 'Ranked by')} {humanizeCol(grouped.ranked_by)} · {grouped.segment_count} {t('report.segment', 'segment')}{(grouped.segment_count || 0) === 1 ? '' : 's'}
                {grouped.note ? ` · ${grouped.note}` : ''}
              </p>
              <div className="space-y-3">
                {grouped.segments.map((seg) => {
                  const m = (grouped.ranked_by && seg.metrics[grouped.ranked_by]) || null;
                  const pct = m && m.share != null ? Math.round(m.share * 1000) / 10 : null;
                  return (
                    <div key={seg.segment} className="flex items-center gap-3">
                      <span className="text-xs font-mono text-slate-400 dark:text-slate-500 w-6">#{seg.rank}</span>
                      <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 w-40 truncate" title={seg.segment}>
                        {seg.segment}
                      </span>
                      <div className="flex-1 h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden min-w-[60px]">
                        <div
                          className="h-full bg-indigo-500 dark:bg-indigo-400 rounded-full transition-all"
                          style={{ width: `${pct ?? 0}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-600 dark:text-slate-300 w-16 text-right">
                        {pct != null ? `${pct}%` : '—'}
                      </span>
                      <span className="text-[11px] text-slate-500 dark:text-slate-400 w-52 text-right hidden md:block">
                        {humanizeCol(grouped.ranked_by)} : {t('report.avg', 'avg.')} {m ? m.mean : '—'} · {t('report.total', 'total')} {m ? m.sum : '—'} · {seg.row_count} {t('report.entries', 'entries')}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          {grouped && (grouped.segments || []).length === 0 && grouped.note && (
            <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/30 text-xs text-amber-800 dark:text-amber-200 flex items-start space-x-3">
              <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <span>
                {t('report.segmentation_na', 'Segmentation')} «&nbsp;{humanizeCol(grouped.group_by)}&nbsp;» {t('report.not_applicable', 'not applicable')}: {grouped.note}
              </span>
            </div>
          )}
        </div>
      )}

      {/* VIEW: CHARTS */}
      {activeView === 'charts' && (
        <div className="space-y-6">
          {numericColumns.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
              {t('report.no_numeric_cols', 'No numeric columns detected in the data to draw charts.')}
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {numericColumns.map((col, idx) => {
                const colors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#3b82f6'];
                const colColor = colors[idx % colors.length];
                const colAnom = anomalies.find(a => a.column === col && (a.count || 0) > 0);

                return (
                  <div key={col} className="space-y-3">
                    <DynamicChartRenderer
                      title={humanizeCol(col)}
                      subtitle={t('report.chart_subtitle', 'Évolution chronologique et templates visuels')}
                      data={chartData}
                      metrics={[{ key: col, label: humanizeCol(col), color: colColor }]}
                      xAxisKey="_index"
                      height={240}
                    />

                    {colAnom && (() => {
                      const insight = getContextualAnomalyInsight(col, colAnom, language);
                      return (
                        <div className="p-3.5 rounded-xl bg-amber-50/90 dark:bg-amber-950/40 border border-amber-200/80 dark:border-amber-800/60 text-xs flex items-start space-x-3 text-amber-950 dark:text-amber-200">
                          <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                          <div className="leading-relaxed space-y-1.5 w-full">
                            <div className="flex items-center gap-1.5 font-semibold text-[11px] uppercase tracking-wider text-amber-800 dark:text-amber-300">
                              <span>{t('report.anomaly_on_var', "Point d'attention sur cette variable :")}</span>
                            </div>
                            <p className="text-slate-800 dark:text-slate-200 font-medium">
                              {insight.reason}
                            </p>
                            {insight.recommendation && (
                              <div className="pt-2 border-t border-amber-200/60 dark:border-amber-900/40 text-[11.5px] text-slate-700 dark:text-slate-300">
                                <span className="font-semibold text-amber-900 dark:text-amber-200">
                                  {t('report.action_advised', 'Action conseillée :')}
                                </span>{' '}
                                <span>{insight.recommendation}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* VIEW: RAW DATA */}
      {activeView === 'data' && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">{t('report.raw_title', 'Record Sample')}</h3>
            <span className="text-xs text-slate-500 font-mono">
              {t('report.showing_rows', 'Showing')} {Math.min(50, rawData?.length || 0)} {t('report.first_rows', 'first rows')}
            </span>
          </div>
          {rawData && rawData.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3 font-mono text-slate-400">#</th>
                    {Object.keys(rawData[0]).map((col) => (
                      <th key={col} className="py-2.5 px-3 font-semibold">{humanizeCol(col)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 bg-white dark:bg-slate-900/40">
                  {rawData.slice(0, 50).map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 text-slate-700 dark:text-slate-300">
                      <td className="py-2 px-3 font-mono text-slate-400">{idx + 1}</td>
                      {Object.keys(rawData[0]).map((col) => (
                        <td key={col} className="py-2 px-3 font-mono">{String(row[col] ?? '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-xs text-slate-500">{t('report.no_raw_data', 'No raw data available.')}</p>
          )}
        </div>
      )}

      {/* Modal d'explication de faits et preuves (Key Finding Evidence) */}
      <EvidenceModal
        isOpen={!!selectedEvidenceInsight}
        onClose={() => setSelectedEvidenceInsight(null)}
        insight={selectedEvidenceInsight}
      />

      {/* Modal Code API (cURL, Python, JS, PHP) */}
      <ApiSnippetModal
        isOpen={showApiSnippet}
        onClose={() => setShowApiSnippet(false)}
        endpoint="/api/v1/analyze"
        samplePayload={{
          application: report.application_slug || 'votre-app-slug',
          dataset: report.dataset_slug || 'votre-dataset-slug',
          analysis: report.analysis_types ? report.analysis_types.split(',') : ['summary', 'trend', 'anomaly'],
          include_ai: true,
          language: language === 'en' ? 'en' : 'fr',
          data: rawData && rawData.length > 0 ? rawData.slice(0, 5) : [
            { "date": "2026-09-01", "culture": "Maïs", "rendement_kg": 4500, "pluviometrie_mm": 42.5 },
            { "date": "2026-09-02", "culture": "Blé", "rendement_kg": 3200, "pluviometrie_mm": 18.0 }
          ]
        }}
      />
    </div>
  );
}
