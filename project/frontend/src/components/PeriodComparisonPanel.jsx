import React from 'react';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldAlert,
  GitCompare,
  Minus
} from 'lucide-react';

function parseAi(raw) {
  if (!raw) return null;
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch {
    return null;
  }
}

export default function PeriodComparisonPanel({ report }) {
  if (!report) return null;

  const ai = parseAi(report.ai_interpretation);
  const improved = report.improved || [];
  const degraded = report.degraded || [];
  const stable = report.stable || [];
  const vigilance = report.vigilance_points || [];

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 transition-colors animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            <GitCompare className="h-4 w-4" />
            <span>Comparatif Temporel Automatique</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
            {report.period_a_label} <span className="text-slate-400 font-normal">vs</span> {report.period_b_label}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {report.period_a_rows} enregistrements ({report.period_a_label}) comparés à {report.period_b_rows} enregistrements ({report.period_b_label})
          </p>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          {degraded.length === 0 && vigilance.length === 0 ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900 text-xs font-semibold">
              <CheckCircle2 className="h-4 w-4" />
              <span>Trajectoire Très Positive</span>
            </span>
          ) : degraded.length > improved.length ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-900 text-xs font-semibold">
              <AlertTriangle className="h-4 w-4" />
              <span>Points de Repli à Traiter</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900 text-xs font-semibold">
              <GitCompare className="h-4 w-4" />
              <span>Évolution Mixte</span>
            </span>
          )}
        </div>
      </div>

      {/* AI Executive Interpretation */}
      {ai ? (
        <div className="space-y-5">
          {ai.summary && (
            <div className="bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
              <div className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1.5 flex items-center space-x-1.5">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Synthèse Décisionnelle de Direction</span>
              </div>
              {ai.summary}
            </div>
          )}

          {/* Key findings & recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {ai.key_findings && ai.key_findings.length > 0 && (
              <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                  <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                  Constats d'Évolution Clés
                </h4>
                <ul className="space-y-2.5">
                  {ai.key_findings.map((f, i) => (
                    <li key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold mt-0.5">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {ai.recommendations && ai.recommendations.length > 0 && (
              <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mr-2" />
                  Actions Prioritaires Recommandées
                </h4>
                <ul className="space-y-2.5">
                  {ai.recommendations.map((r, i) => (
                    <li key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold mt-0.5">•</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Action plan */}
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
        </div>
      ) : (
        <div className="p-4 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
          {report.executive_summary}
        </div>
      )}

      {/* The 3 Core Pillars */}
      <div className="space-y-4 pt-2">
        {/* 1. CE QUI S'EST AMÉLIORÉ */}
        <div className="p-5 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-200 flex items-center">
              <TrendingUp className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mr-2" />
              Ce qui s'est amélioré
            </h3>
            <span className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-300">
              {improved.length === 0 ? 'Aucun progrès notable' : 'Gains constatés'}
            </span>
          </div>

          {improved.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {improved.map((item, idx) => (
                <div key={idx} className="p-3 bg-white dark:bg-slate-900 rounded-lg border border-emerald-200/60 dark:border-emerald-900/40 text-xs">
                  <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-100 mb-1">
                    <span>{item.label}</span>
                    {item.change_pct != null && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 font-mono text-[11px]">
                        {item.change_pct > 0 ? `+${item.change_pct}%` : `${item.change_pct}%`}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                    {item.explanation}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">Aucun indicateur n'a enregistré d'amélioration significative sur cette période.</p>
          )}
        </div>

        {/* 2. CE QUI S'EST DÉGRADÉ */}
        <div className="p-5 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200/80 dark:border-rose-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-rose-800 dark:text-rose-200 flex items-center">
              <TrendingDown className="h-4 w-4 text-rose-600 dark:text-rose-400 mr-2" />
              Ce qui s'est dégradé
            </h3>
            <span className="text-[11px] font-semibold text-rose-700 dark:text-rose-300">
              {degraded.length === 0 ? 'Aucun recul constaté' : 'Points en repli'}
            </span>
          </div>

          {degraded.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {degraded.map((item, idx) => (
                <div key={idx} className="p-3 bg-white dark:bg-slate-900 rounded-lg border border-rose-200/60 dark:border-rose-900/40 text-xs">
                  <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-100 mb-1">
                    <span>{item.label}</span>
                    {item.change_pct != null && (
                      <span className="px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-900/60 text-rose-700 dark:text-rose-300 font-mono text-[11px]">
                        {item.change_pct > 0 ? `+${item.change_pct}%` : `${item.change_pct}%`}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                    {item.explanation}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">Excellente nouvelle : aucun indicateur n'a subi de dégradation notable sur cette période.</p>
          )}
        </div>

        {/* 3. NOUVEAUX POINTS DE VIGILANCE */}
        <div className="p-5 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-200 flex items-center">
              <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 mr-2" />
              Nouveaux Points de Vigilance
            </h3>
            <span className="text-[11px] font-semibold text-amber-700 dark:text-amber-300">
              {vigilance.length === 0 ? 'Aucune instabilité' : 'Comportements atypiques récents'}
            </span>
          </div>

          {vigilance.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {vigilance.map((v, idx) => (
                <div key={idx} className="p-3 bg-white dark:bg-slate-900 rounded-lg border border-amber-200/60 dark:border-amber-900/40 text-xs">
                  <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-100 mb-1">
                    <span>{v.label}</span>
                    <span className="px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-300 text-[10px] uppercase font-bold">
                      {v.severity === 'high' ? 'Alerte' : 'Vigilance'}
                    </span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                    {v.description}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">Aucune nouvelle anomalie ou instabilité inhabituelle apparue sur {report.period_b_label}.</p>
          )}
        </div>

        {/* Indicateurs Stables */}
        {stable.length > 0 && (
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 text-xs">
            <div className="flex items-center space-x-2 text-slate-600 dark:text-slate-400 font-semibold mb-2">
              <Minus className="h-3.5 w-3.5 text-slate-400" />
              <span>Indicateurs Constants &amp; Stables ({stable.length})</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {stable.map((s, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px] text-slate-700 dark:text-slate-300" title={s.explanation}>
                  {s.label} ({s.change_pct != null && s.change_pct > 0 ? `+${s.change_pct}%` : `${s.change_pct}%`})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
