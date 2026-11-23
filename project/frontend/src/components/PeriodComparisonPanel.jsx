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
import { useLanguage } from '../i18n/LanguageContext';

function parseAi(raw) {
  if (!raw) return null;
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch {
    return null;
  }
}

export default function PeriodComparisonPanel({ report }) {
  const { t } = useLanguage();
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
            <span>{t('period_compare.header_badge', 'Comparatif Temporel Automatique')}</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
            {report.period_a_label} <span className="text-slate-400 font-normal">vs</span> {report.period_b_label}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {t('period_compare.records_compared', '{a_rows} enregistrements ({a_label}) comparés à {b_rows} enregistrements ({b_label})')
              .replace('{a_rows}', report.period_a_rows)
              .replace('{a_label}', report.period_a_label)
              .replace('{b_rows}', report.period_b_rows)
              .replace('{b_label}', report.period_b_label)}
          </p>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          {degraded.length === 0 && vigilance.length === 0 ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900 text-xs font-semibold">
              <CheckCircle2 className="h-4 w-4" />
              <span>{t('period_compare.badge_very_positive', 'Trajectoire Très Positive')}</span>
            </span>
          ) : degraded.length > improved.length ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-900 text-xs font-semibold">
              <AlertTriangle className="h-4 w-4" />
              <span>{t('period_compare.badge_retreat', 'Points de Repli à Traiter')}</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900 text-xs font-semibold">
              <GitCompare className="h-4 w-4" />
              <span>{t('period_compare.badge_mixed', 'Évolution Mixte')}</span>
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
                <span>{t('period_compare.executive_summary_title', 'Synthèse Décisionnelle de Direction')}</span>
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
                  {t('period_compare.key_findings_title', "Constats d'Évolution Clés")}
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
                  {t('period_compare.priority_actions_title', 'Actions Prioritaires Recommandées')}
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
                {t('period_compare.action_plan_title', "Plan d'Action Décisionnel")}
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

      {/* The Core Face-à-Face: What Improved vs What Degraded */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 pt-2">
        {/* 1. CE QUI S'EST AMÉLIORÉ */}
        <div className="p-5 rounded-2xl bg-gradient-to-b from-emerald-50/70 to-emerald-50/20 dark:from-emerald-950/30 dark:to-emerald-950/10 border border-emerald-200/90 dark:border-emerald-800/50 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between pb-3.5 mb-3.5 border-b border-emerald-200/60 dark:border-emerald-900/50">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-xl bg-emerald-600/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
                  <TrendingUp className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 dark:text-emerald-200">
                    {t('period_compare.improved_title', "Ce qui s'est amélioré")}
                  </h3>
                  <p className="text-[11px] text-emerald-700/80 dark:text-emerald-400/80">
                    {t('period_compare.improved_gains', 'Gains constatés')}
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 font-bold text-xs">
                +{improved.length}
              </span>
            </div>

            {improved.length > 0 ? (
              <div className="space-y-2.5">
                {improved.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-white dark:bg-slate-900 rounded-xl border border-emerald-200/80 dark:border-emerald-900/60 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-700 transition-all"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <span className="font-bold text-sm text-slate-800 dark:text-slate-100 block truncate">
                          {item.label}
                        </span>
                        <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
                          {item.explanation}
                        </p>
                      </div>
                      {item.change_pct != null && (
                        <div className="shrink-0 flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200/80 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 font-bold font-mono text-sm shadow-xs">
                          <TrendingUp className="h-3.5 w-3.5" />
                          <span>{item.change_pct > 0 ? `+${item.change_pct}%` : `${item.change_pct}%`}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-500 dark:text-slate-400 italic">
                {t('period_compare.improved_empty', "Aucun indicateur n'a enregistré d'amélioration significative sur cette période.")}
              </div>
            )}
          </div>
        </div>

        {/* 2. CE QUI S'EST DÉGRADÉ */}
        <div className="p-5 rounded-2xl bg-gradient-to-b from-rose-50/70 to-rose-50/20 dark:from-rose-950/30 dark:to-rose-950/10 border border-rose-200/90 dark:border-rose-800/50 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between pb-3.5 mb-3.5 border-b border-rose-200/60 dark:border-rose-900/50">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-xl bg-rose-600/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center font-bold">
                  <TrendingDown className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-rose-900 dark:text-rose-200">
                    {t('period_compare.degraded_title', "Ce qui s'est dégradé")}
                  </h3>
                  <p className="text-[11px] text-rose-700/80 dark:text-rose-400/80">
                    {t('period_compare.degraded_points', 'Points en repli')}
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-rose-100 dark:bg-rose-900/60 text-rose-800 dark:text-rose-200 font-bold text-xs">
                {degraded.length > 0 ? `-${degraded.length}` : '0'}
              </span>
            </div>

            {degraded.length > 0 ? (
              <div className="space-y-2.5">
                {degraded.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-white dark:bg-slate-900 rounded-xl border border-rose-200/80 dark:border-rose-900/60 shadow-xs hover:border-rose-300 dark:hover:border-rose-700 transition-all"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <span className="font-bold text-sm text-slate-800 dark:text-slate-100 block truncate">
                          {item.label}
                        </span>
                        <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
                          {item.explanation}
                        </p>
                      </div>
                      {item.change_pct != null && (
                        <div className="shrink-0 flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200/80 dark:border-rose-800/60 text-rose-700 dark:text-rose-300 font-bold font-mono text-sm shadow-xs">
                          <TrendingDown className="h-3.5 w-3.5" />
                          <span>{item.change_pct > 0 ? `+${item.change_pct}%` : `${item.change_pct}%`}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-500 dark:text-slate-400 italic">
                {t('period_compare.degraded_empty', "Excellente nouvelle : aucun indicateur n'a subi de dégradation notable sur cette période.")}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. NOUVEAUX POINTS DE VIGILANCE & STABLE INDICATORS */}
      <div className="space-y-4 pt-1">

        {/* 3. NOUVEAUX POINTS DE VIGILANCE */}
        {vigilance.length > 0 ? (
          <div className="p-5 rounded-2xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-900/40 space-y-3 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-amber-200/60 dark:border-amber-900/40">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-xl bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center font-bold">
                  <AlertTriangle className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-amber-900 dark:text-amber-200">
                    {t('period_compare.vigilance_title', 'Nouveaux Points de Vigilance')}
                  </h3>
                  <p className="text-[11px] text-amber-700/80 dark:text-amber-400/80">
                    {t('period_compare.vigilance_points', 'Comportements atypiques récents')}
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200 font-bold text-xs">
                {vigilance.length}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {vigilance.map((v, idx) => (
                <div key={idx} className="p-3.5 bg-white dark:bg-slate-900 rounded-xl border border-amber-200/70 dark:border-amber-900/50 shadow-xs text-xs space-y-1">
                  <div className="flex items-center justify-between font-semibold text-slate-800 dark:text-slate-100">
                    <span className="text-sm">{v.label}</span>
                    <span className="px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-300 text-[11px] font-semibold">
                      {v.severity === 'high' ? t('period_compare.severity_alert', 'Alerte') : t('period_compare.severity_vigilance', 'Vigilance')}
                    </span>
                  </div>
                  <p className="text-slate-500 dark:text-slate-400 text-xs">
                    {v.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
              <span>
                {t('period_compare.vigilance_empty', 'Aucune nouvelle anomalie ou instabilité inhabituelle apparue sur {label}.').replace('{label}', report.period_b_label)}
              </span>
            </div>
            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 shrink-0">
              {t('period_compare.vigilance_none', 'Aucune instabilité')}
            </span>
          </div>
        )}

        {/* Indicateurs Stables */}
        {stable.length > 0 && (
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800 text-xs">
            <div className="flex items-center space-x-2 text-slate-600 dark:text-slate-400 font-semibold mb-2">
              <Minus className="h-3.5 w-3.5 text-slate-400" />
              <span>{t('period_compare.stable_title', 'Indicateurs Constants & Stables ({count})').replace('{count}', stable.length)}</span>
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
