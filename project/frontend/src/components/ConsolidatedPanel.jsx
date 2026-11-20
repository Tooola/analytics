import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Sparkles,
  Clock,
  ArrowRight,
  TrendingUp,
  CheckCircle,
  Layers,
  Lightbulb,
} from 'lucide-react';

function humanizeCol(name) {
  if (!name) return name;
  const unitMap = {
    '_kg': ' (kg)', '_mm': ' (mm)', '_c': ' (°C)', '_pct': ' (%)',
    '_percent': ' (%)', '_eur': ' (€)', '_euro': ' (€)', '_usd': ' ($)',
    '_fcfa': ' (FCFA)', '_cfa': ' (FCFA)',
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

const VERDICTS = {
  positif: {
    label: 'Dynamique globale positive',
    cls: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900',
    Icon: CheckCircle2,
  },
  equilibre: {
    label: 'Équilibre relatif',
    cls: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-900',
    Icon: CheckCircle2,
  },
  tension: {
    label: 'Tensions entre indicateurs',
    cls: 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-900',
    Icon: AlertTriangle,
  },
  surveiller: {
    label: 'Points à surveiller',
    cls: 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-900',
    Icon: ShieldAlert,
  },
};

function parseAi(raw) {
  if (!raw) return null;
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch {
    return null;
  }
}

function getAnomalyReason(anom) {
  if (anom.reason) return anom.reason;
  return "Niveau atypique constaté s'éloignant significativement de la dynamique normale observée sur la période.";
}

function getAnomalyRecommendation(anom) {
  if (anom.recommendation) return anom.recommendation;
  return "Contrôler les enregistrements sources à cette date pour confirmer la réalité de cette variation et vérifier s'il s'agit d'un événement opérationnel exceptionnel ou d'une anomalie de saisie.";
}

export default function ConsolidatedPanel({ res }) {
  const syn = res?.synthesis;
  if (!syn) return null;

  const ai = parseAi(res?.ai_interpretation);
  const verdict = VERDICTS[syn.verdict] || VERDICTS.equilibre;
  const VIcon = verdict.Icon;

  // Extraire toutes les anomalies réelles des différents jeux de données
  const allAnomalies = [];
  const allCausality = [];
  if (res?.results) {
    for (const [slug, dsResult] of Object.entries(res.results)) {
      const dsName = syn.dataset_names?.[slug] || slug;
      const anomList = dsResult?.anomaly || [];
      for (const anom of anomList) {
        if ((anom.count || 0) > 0) {
          allAnomalies.push({
            datasetSlug: slug,
            datasetName: dsName,
            column: anom.column,
            count: anom.count,
            reason: anom.reason,
            recommendation: anom.recommendation,
            items: anom.anomalies || [],
          });
        }
      }
      const causalityList = dsResult?.causality || [];
      for (const c of causalityList) {
        if (c.explanation) {
          allCausality.push({
            datasetSlug: slug,
            datasetName: dsName,
            target: c.target,
            driver: c.driver,
            explanation: c.explanation,
          });
        }
      }
    }
  }

  const hasAnomalies = allAnomalies.length > 0;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 transition-colors">
      {/* Header + verdict exécutif */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            <Layers className="h-3.5 w-3.5" />
            <span>Synthèse Multi-Jeux Décisionnelle ({syn.datasets_analyzed} sources analysées)</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
            {res.application}
            {syn.join_key && (
              <span className="text-xs font-normal text-slate-500 dark:text-slate-400 ml-2">
                • {syn.total_rows} enregistrements combinés
              </span>
            )}
          </h2>
        </div>
        <span className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-xl border text-xs font-semibold ${verdict.cls}`}>
          <VIcon className="h-4 w-4" />
          <span>{verdict.label}</span>
        </span>
      </div>

      {/* Bloc Exécutif IA (Principal) */}
      {ai && (
        <div className="space-y-5">
          {/* Synthèse de Direction */}
          {ai.summary && (
            <div className="bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
              <div className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1.5 flex items-center space-x-1.5">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Synthèse Globale de Direction</span>
              </div>
              {ai.summary}
            </div>
          )}

          {/* Grille : Constats Majeurs & Recommandations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Constats Majeurs */}
            {ai.key_findings && ai.key_findings.length > 0 && (
              <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                  <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                  Constats Majeurs Entre les Jeux
                </h4>
                <ul className="space-y-2.5">
                  {ai.key_findings.map((finding, idx) => (
                    <li key={idx} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold mt-0.5">•</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommandations Décisionnelles */}
            {ai.recommendations && ai.recommendations.length > 0 && (
              <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                  <CheckCircle className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mr-2" />
                  {hasAnomalies ? 'Actions Correctives Recommandées' : 'Recommandations Opérationnelles'}
                </h4>
                <ul className="space-y-2.5">
                  {ai.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold mt-0.5">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Plan d'action */}
          {ai.action_plan && ai.action_plan.length > 0 && (
            <div className="pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                <Clock className="h-4 w-4 text-sky-600 dark:text-sky-400 mr-2" />
                Plan d'Action Décisionnel
              </h4>
              <div className="space-y-2">
                {ai.action_plan.map((step, idx) => {
                  const cleanStep = step.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();
                  return (
                    <div key={idx} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start space-x-3">
                      <ArrowRight className="h-4 w-4 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                      <span className="leading-relaxed">{cleanStep}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Évaluation Globale des Risques */}
          {ai.risk_assessment && (
            <div className="p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/30 flex items-start space-x-3 text-xs text-amber-800 dark:text-amber-200">
              <ShieldAlert className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold uppercase tracking-wider text-[11px] block">Évaluation Globale des Risques :</span>
                <span className="leading-relaxed">{ai.risk_assessment}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Facteurs d'explication / Moteurs multi-jeux */}
      {allCausality.length > 0 && (
        <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center">
            <Lightbulb className="h-4 w-4 text-amber-500 mr-2 shrink-0" />
            Facteurs d'Explication &amp; Moteurs de Variation
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {allCausality.map((driver, idx) => (
              <div key={idx} className="p-3 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start space-x-2.5">
                <span className="text-amber-500 font-bold mt-0.5">•</span>
                <div className="leading-relaxed">
                  <span className="font-semibold text-slate-900 dark:text-slate-200 block text-[11px] text-slate-500 mb-0.5">{driver.datasetName}</span>
                  <span>{driver.explanation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section Points d'Attention & Actions Correctives */}
      {hasAnomalies ? (
        <div className="mt-4 p-5 rounded-2xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-800/40 space-y-4">
          <div className="flex items-center space-x-2 text-amber-900 dark:text-amber-200 font-bold text-xs uppercase tracking-wider">
            <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" />
            <span>Points de Vigilance &amp; Actions Correctives Recommandées</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {allAnomalies.map((anom, idx) => (
              <div key={idx} className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-amber-200/60 dark:border-amber-800/30 text-xs shadow-sm space-y-2">
                <div className="font-bold text-slate-900 dark:text-white text-xs">
                  {anom.datasetName} — {humanizeCol(anom.column)}
                </div>
                <div className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                  <span className="font-semibold text-amber-800 dark:text-amber-300">Constat : </span>
                  {getAnomalyReason(anom)}
                </div>
                <div className="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed pt-1.5 border-t border-slate-100 dark:border-slate-800">
                  <span className="font-semibold text-emerald-700 dark:text-emerald-400">Action conseillée : </span>
                  {getAnomalyRecommendation(anom)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="p-3 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/40 text-xs text-emerald-800 dark:text-emerald-200 flex items-center space-x-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>Données saines : aucune instabilité anormale détectée sur l'ensemble des jeux analysés.</span>
        </div>
      )}
    </div>
  );
}
