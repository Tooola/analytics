import React, { useState } from 'react';
import { Clock, Trash2, ChevronDown, ChevronRight } from 'lucide-react';
import BiReport from '../components/BiReport';
import ConsolidatedPanel from '../components/ConsolidatedPanel';
import {
  listHistory,
  deleteHistoryEntry,
  clearHistory,
} from '../api/history';

/**
 * History of the analyses run from this browser: every completed run is
 * saved with its FULL response (results, insights, AI verdict, and for the
 * consolidated pass the synthesis + cross links), so reopening an entry
 * renders the exact report that was on screen when it was run.
 */
const KINDS = {
  quick: 'Test rapide',
  single: 'Analyse',
  multi: 'Consolidée',
};

const VERDICTS = {
  positif: 'positif',
  equilibre: 'équilibre',
  tension: 'tension',
  surveiller: 'à surveiller',
};

export default function History() {
  // Fresh read on mount: the tab unmounts when leaving, so every visit
  // picks up the latest runs.
  const [entries, setEntries] = useState(listHistory);
  const [openId, setOpenId] = useState(null);

  const refresh = () => {
    setEntries(listHistory());
  };

  const handleDelete = (id) => {
    deleteHistoryEntry(id);
    refresh();
    if (openId === id) setOpenId(null);
  };

  const handleClear = () => {
    if (!window.confirm("Supprimer toute l'historique des analyses ?")) return;
    clearHistory();
    setEntries([]);
    setOpenId(null);
  };

  const fmtDate = (ts) =>
    new Date(ts).toLocaleString('fr-FR', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });

  const aiBadge = (status) => {
    if (status === 'ok') {
      return (
        <span className="shrink-0 inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900">
          IA : ok
        </span>
      );
    }
    if (status === 'error') {
      return (
        <span className="shrink-0 inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-900">
          IA : erreur
        </span>
      );
    }
    return (
      <span className="shrink-0 inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
        sans IA
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="h-5 w-5 text-indigo-500" />
            Historique des analyses
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {entries.length} analyse{entries.length === 1 ? '' : 's'} conservée
            {entries.length === 1 ? '' : 's'} dans ce navigateur — les 50
            dernières, avec la synthèse consolidée et l'avis IA.
          </p>
        </div>
        {entries.length > 0 && (
          <button
            onClick={handleClear}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-semibold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Vider l'historique
          </button>
        )}
      </header>

      {entries.length === 0 ? (
        <div className="p-10 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 text-center text-sm text-slate-500 dark:text-slate-400">
          Aucune analyse pour l'instant — lancez une évaluation depuis
          «&nbsp;Test Rapide&nbsp;» ou «&nbsp;Analyse Avancée&nbsp;» : elle
          apparaîtra ici.
        </div>
      ) : (
        <div className="space-y-3">
          {entries.map((e) => {
            const open = openId === e.id;
            return (
              <div
                key={e.id}
                className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 overflow-hidden"
              >
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3">
                  <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900">
                    {KINDS[e.kind] || e.kind}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                      {e.title}
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      {fmtDate(e.savedAt)}
                      {typeof e.rows === 'number' && (
                        <> · {e.rows} ligne{e.rows === 1 ? '' : 's'}</>
                      )}
                      {e.joinKey && <> · alignés sur «&nbsp;{e.joinKey}&nbsp;»</>}
                      {e.groupBy && (
                        <> · segments par «&nbsp;{e.groupBy}&nbsp;»</>
                      )}
                    </p>
                  </div>
                  {e.verdict && (
                    <span className="shrink-0 text-[11px] font-medium text-slate-600 dark:text-slate-300">
                      Verdict : {VERDICTS[e.verdict] || e.verdict}
                    </span>
                  )}
                  {aiBadge(e.aiStatus)}
                  <div className="shrink-0 flex items-center gap-1.5">
                    <button
                      onClick={() => handleDelete(e.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                      title="Supprimer cette entrée"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => setOpenId(open ? null : e.id)}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 transition-colors"
                    >
                      {open ? (
                        <>
                          <ChevronDown className="h-3.5 w-3.5" />
                          Masquer
                        </>
                      ) : (
                        <>
                          <ChevronRight className="h-3.5 w-3.5" />
                          Rouvrir
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {open && (
                  <div className="border-t border-slate-200 dark:border-slate-800 p-4 space-y-6 bg-slate-50/50 dark:bg-slate-950/30">
                    {e.kind === 'multi' ? (
                      <>
                        <ConsolidatedPanel res={e.res} />
                        {Object.keys(e.res?.results || {}).map((slug) => (
                          <BiReport
                            key={slug}
                            report={{
                              label: `${e.app} / ${slug}`,
                              results: e.res.results[slug] || {},
                              insights: e.res.insights?.[slug] || [],
                              row_count: e.payloads?.[slug]?.length || 0,
                              ai_interpretation: null,
                            }}
                            rawData={e.payloads?.[slug] || []}
                          />
                        ))}
                      </>
                    ) : (
                      <BiReport report={e.report} rawData={e.payloads || []} />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
