import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Link2,
  Sparkles,
} from 'lucide-react';

/**
 * Consolidated panel rendered for POST /analyze/multi responses:
 * verdict badge + French synthesis summary + trends per dataset +
 * cross-dataset links + the single AI interpretation of the whole picture.
 */
const VERDICTS = {
  positif: {
    label: 'Dynamique positive',
    cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900',
    Icon: CheckCircle2,
  },
  equilibre: {
    label: 'Équilibre relatif',
    cls: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border-indigo-200 dark:border-indigo-900',
    Icon: Activity,
  },
  tension: {
    label: 'Tensions détectées',
    cls: 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-900',
    Icon: AlertTriangle,
  },
  surveiller: {
    label: 'Points à surveiller',
    cls: 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-900',
    Icon: ShieldAlert,
  },
};

const TRENDS = {
  up: { label: 'hausse', Icon: ArrowUpRight, cls: 'text-emerald-600 dark:text-emerald-400' },
  down: { label: 'baisse', Icon: ArrowDownRight, cls: 'text-rose-600 dark:text-rose-400' },
  stable: { label: 'stable', Icon: Minus, cls: 'text-slate-500 dark:text-slate-400' },
};

function parseAi(raw) {
  if (!raw) return null;
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch {
    return null;
  }
}

export default function ConsolidatedPanel({ res }) {
  const syn = res?.synthesis;
  if (!syn) return null;

  const links = res?.cross_correlations || [];
  const ai = parseAi(res?.ai_interpretation);
  const verdict = VERDICTS[syn.verdict] || VERDICTS.equilibre;
  const VIcon = verdict.Icon;
  const shownLinks = links.slice(0, 6);

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 transition-colors">
      {/* Header + verdict */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            <Link2 className="h-3.5 w-3.5" />
            <span>Analyse Consolidée — {syn.datasets_analyzed} jeux en un passage</span>
          </div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white mt-1">
            {res.application}
            {syn.join_key && (
              <span className="text-xs font-normal text-slate-500 dark:text-slate-400 ml-2">
                alignés sur « {syn.join_key} » • {syn.total_rows} lignes
              </span>
            )}
          </h2>
        </div>
        <span className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold ${verdict.cls}`}>
          <VIcon className="h-3.5 w-3.5" />
          <span>{verdict.label}</span>
        </span>
      </div>

      {/* Narrative */}
      <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-3">
        {syn.summary}
      </p>

      {/* Trends per dataset */}
      {Object.keys(syn.trends || {}).length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Tendances :</span>
          {Object.entries(syn.trends).map(([slug, dir]) => {
            const T = TRENDS[dir] || TRENDS.stable;
            return (
              <span key={slug} title={slug} className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300">
                <span>{syn.dataset_names?.[slug] || slug}</span>
                <T.Icon className={`h-3.5 w-3.5 ${T.cls}`} />
                <span className={T.cls}>{T.label}</span>
              </span>
            );
          })}
          {syn.divergent && (
            <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-amber-100 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-900 text-xs font-semibold text-amber-700 dark:text-amber-300">
              divergence entre jeux
            </span>
          )}
        </div>
      )}

      {/* Risks */}
      {(syn.risks || []).length > 0 && (
        <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-xs text-rose-700 dark:text-rose-300 space-y-1">
          {syn.risks.map((risk) => (
            <div key={risk} className="flex items-center space-x-2">
              <ShieldAlert className="h-3.5 w-3.5 shrink-0" />
              <span>{risk}</span>
            </div>
          ))}
        </div>
      )}

      {/* Cross-dataset links */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
          <Link2 className="h-3.5 w-3.5" />
          <span>Liens entre jeux de données ({links.length})</span>
        </div>
        {links.length === 0 ? (
          <p className="text-xs text-slate-500 dark:text-slate-400 italic">
            {syn.join_key
              ? `Aucun lien significatif sur la période — vérifiez que « ${syn.join_key} » est présent dans ≥ 2 jeux avec ≥ 5 lignes alignées.`
              : "Aucun lien calculé — renseignez la clé d'alignement (ex. « mois ») avec ≥ 2 jeux partageant cette colonne."}
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-slate-400 dark:text-slate-500 border-b border-slate-200 dark:border-slate-800">
                  <th className="py-1.5 pr-3 font-medium">Source</th>
                  <th className="py-1.5 pr-3 font-medium">Cible</th>
                  <th className="py-1.5 pr-3 font-medium">r</th>
                  <th className="py-1.5 font-medium">Lecture</th>
                </tr>
              </thead>
              <tbody>
                {shownLinks.map((l, idx) => (
                  <tr key={`${l.dataset1}-${l.column1}-${idx}`} className="border-b border-slate-100 dark:border-slate-800/60 text-slate-700 dark:text-slate-300">
                    <td className="py-1.5 pr-3 font-mono">{l.dataset1}.{l.column1}</td>
                    <td className="py-1.5 pr-3 font-mono">{l.dataset2}.{l.column2}</td>
                    <td className={`py-1.5 pr-3 font-semibold ${Math.abs(l.coefficient) >= 0.7 ? 'text-indigo-600 dark:text-indigo-400' : ''}`}>
                      {l.coefficient}
                    </td>
                    <td className="py-1.5">
                      {l.relationship === 'positive' ? 'même sens' : 'sens inverse'}
                      <span className="text-slate-400 dark:text-slate-500 ml-1">
                        ({l.strength === 'strong' ? 'fort' : 'modéré'})
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {links.length > shownLinks.length && (
              <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1.5">
                +{links.length - shownLinks.length} autre{links.length - shownLinks.length > 1 ? 's' : ''} lien{links.length - shownLinks.length > 1 ? 's' : ''} significatif{links.length - shownLinks.length > 1 ? 's' : ''}
              </p>
            )}
          </div>
        )}
      </div>

      {/* One AI interpretation over the whole picture */}
      {ai && (
        <div className="rounded-xl border border-indigo-200 dark:border-indigo-900/60 bg-indigo-50/60 dark:bg-indigo-950/30 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Interprétation IA — lecture globale</span>
            </div>
            <span className="text-[11px] text-indigo-500 dark:text-indigo-400 font-mono">
              {ai.provider}{typeof ai.confidence === 'number' ? ` • ${Math.round(ai.confidence * 100)}%` : ''}
            </span>
          </div>
          {ai.summary && <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{ai.summary}</p>}
          {ai.key_findings?.length > 0 && (
            <ul className="text-xs text-slate-600 dark:text-slate-300 space-y-1 list-disc list-inside">
              {ai.key_findings.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          )}
          {ai.recommendations?.length > 0 && (
            <ul className="text-xs text-slate-600 dark:text-slate-300 space-y-1 list-disc list-inside">
              {ai.recommendations.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
