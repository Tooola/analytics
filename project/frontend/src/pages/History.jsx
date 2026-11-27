import React, { useState, useEffect, useMemo } from 'react';
import {
  Clock,
  ChevronDown,
  ChevronRight,
  GitCompare,
  Filter,
  CheckSquare,
  Square,
  RefreshCw,
  User,
  Database,
  X,
  CalendarDays,
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowUpDown,
} from 'lucide-react';
import BiReport from '../components/BiReport';
import ConsolidatedPanel from '../components/ConsolidatedPanel';
import PeriodComparisonPanel from '../components/PeriodComparisonPanel';
import { useLanguage } from '../i18n/LanguageContext';
import { api } from '../api/client';
import { listHistory } from '../api/history';

export default function History({ currentUser }) {
  const { language } = useLanguage();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const [comparing, setComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState(null);

  // Filtres — changements instantanés, pas de bouton
  const [filterPeriod, setFilterPeriod] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortOrder] = useState('desc'); // DESC = plus récente en premier (fixe)

  /* ─── Chargement ─────────────────────────────────────────── */
  const loadHistory = async () => {
    setLoading(true);
    try {
      const dbRuns = await api.getAnalysisRuns(200);
      const localEntries = listHistory() || [];
      const localMap = new Map(localEntries.map((e) => [e.id, e]));

      const merged = (dbRuns || []).map((run) => {
        const local = localMap.get(run.id);
        let parsedReport = local ? local.report : null;
        if (!parsedReport && run.result) {
          try {
            const raw = typeof run.result === 'string' ? JSON.parse(run.result) : run.result;
            parsedReport = {
              label: run.label || raw?.label || 'Analyse',
              row_count: run.row_count,
              results: raw,
              ai_interpretation: run.ai_interpretation,
              ai_status: run.has_ai ? 'ok' : 'none',
            };
          } catch {
            parsedReport = null;
          }
        }

        return {
          id: run.id,
          title: run.label || `${run.application_name || 'Application'} / ${run.dataset_name || 'Jeu de données'}`,
          savedAt: new Date(run.created_at).getTime(),
          rows: run.row_count,
          kind: run.dataset_name?.includes('consolidated') ? 'multi' : 'single',
          operator_username: run.operator_username || currentUser?.username || 'Admin',
          status: run.status,
          hasAi: run.has_ai,
          aiStatus: run.has_ai ? 'ok' : 'none',
          payloads: local ? local.payloads : null,
          report: parsedReport,
          isDb: true,
        };
      });

      // Entrées locales absentes de la DB (tests rapides hors-ligne)
      localEntries.forEach((loc) => {
        if (!merged.some((m) => m.id === loc.id)) {
          merged.push({
            ...loc,
            isDb: false,
            operator_username: loc.operator_username || currentUser?.username || 'Admin',
          });
        }
      });

      // Tri DESC — plus récente en premier
      merged.sort((a, b) => (b.savedAt || 0) - (a.savedAt || 0));
      setEntries(merged);
    } catch {
      setEntries(listHistory() || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  /* ─── Filtrage instantané (computed) ─────────────────────── */
  const filteredEntries = useMemo(() => {
    return entries.filter((e) => {
      const date = new Date(e.savedAt || Date.now());
      const now = new Date();

      // Filtre rapide par période
      if (filterPeriod !== 'all') {
        if (filterPeriod === 'this_month') {
          if (date.getMonth() !== now.getMonth() || date.getFullYear() !== now.getFullYear())
            return false;
        }
        if (filterPeriod === 'last_month') {
          const pm = now.getMonth() === 0 ? 11 : now.getMonth() - 1;
          const py = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
          if (date.getMonth() !== pm || date.getFullYear() !== py) return false;
        }
        if (filterPeriod === 'last_7') {
          const d7 = new Date(now);
          d7.setDate(d7.getDate() - 7);
          if (date < d7) return false;
        }
        if (filterPeriod === 'last_30') {
          const d30 = new Date(now);
          d30.setDate(d30.getDate() - 30);
          if (date < d30) return false;
        }
      }

      // Filtre date personnalisée de → à
      if (dateFrom) {
        const from = new Date(dateFrom);
        from.setHours(0, 0, 0, 0);
        if (date < from) return false;
      }
      if (dateTo) {
        const to = new Date(dateTo);
        to.setHours(23, 59, 59, 999);
        if (date > to) return false;
      }

      return true;
    });
  }, [entries, filterPeriod, dateFrom, dateTo, sortOrder]);

  /* ─── Sélection pour comparaison ─────────────────────────── */
  const toggleSelect = (id) =>
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );

  const handleLaunchComparison = async () => {
    if (selectedIds.length < 2) return;
    const sel = entries
      .filter((e) => selectedIds.includes(e.id))
      .sort((a, b) => (a.savedAt || 0) - (b.savedAt || 0));

    setComparing(true);
    try {
      const periods = sel.map((e) => ({
        label: e.title || `Analyse du ${new Date(e.savedAt).toLocaleDateString('fr-FR')}`,
        data: Array.isArray(e.payloads) ? e.payloads : [],
      }));
      const valid = periods.filter((p) => p.data.length > 0);
      if (valid.length >= 2) {
        const res = await api.quickCompareMulti({
          periods: valid,
          label: `Comparatif ${valid.map((p) => p.label).join(' vs ')}`,
        });
        setComparisonResult(res);
      } else {
        alert(
          "Pour comparer, les analyses doivent contenir les données brutes (lancées depuis le Test Rapide ou les formulaires d'analyse)."
        );
      }
    } catch (err) {
      alert('Erreur lors de la comparaison : ' + err.message);
    } finally {
      setComparing(false);
    }
  };

  /* ─── Helpers ─────────────────────────────────────────────── */
  const fmtDate = (ts) =>
    new Date(ts).toLocaleString(language === 'en' ? 'en-US' : 'fr-FR', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });

  const hasCustomDate = dateFrom || dateTo;
  const clearFilters = () => {
    setFilterPeriod('all');
    setDateFrom('');
    setDateTo('');
  };

  /* ─── Rendu ─────────────────────────────────────────────────── */
  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Clock className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Historique des analyses
            </h1>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Partagé entre tous les administrateurs · Stockage persistant en base de données
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Rafraîchir */}
          <button
            onClick={loadHistory}
            className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            title="Rafraîchir depuis la base de données"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin text-indigo-600' : ''}`} />
          </button>

          {/* Bouton Comparer */}
          {selectedIds.length >= 2 && (
            <button
              onClick={handleLaunchComparison}
              disabled={comparing}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors disabled:opacity-50"
            >
              <GitCompare className="h-3.5 w-3.5" />
              <span>
                {comparing ? 'Comparaison...' : `Comparer (${selectedIds.length})`}
              </span>
            </button>
          )}
        </div>
      </div>

      {/* ── Barre de filtres instantanés ── */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 space-y-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
          <Filter className="h-3.5 w-3.5 text-indigo-500" />
          <span>Filtres instantanés</span>
          {(filterPeriod !== 'all' || hasCustomDate) && (
            <button
              onClick={clearFilters}
              className="ml-auto flex items-center gap-1 text-[11px] text-rose-500 hover:text-rose-700 dark:hover:text-rose-300 font-normal"
            >
              <X className="h-3 w-3" />
              Effacer les filtres
            </button>
          )}
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          {/* Filtre rapide par période */}
          <div className="flex flex-wrap gap-2">
            {[
              { value: 'all', label: 'Tout' },
              { value: 'last_7', label: '7 jours' },
              { value: 'last_30', label: '30 jours' },
              { value: 'this_month', label: 'Ce mois' },
              { value: 'last_month', label: 'Mois passé' },
            ].map(({ value, label }) => (
              <button
                key={value}
                onClick={() => {
                  setFilterPeriod(value);
                  // Effacer le filtre date si on choisit un raccourci
                  setDateFrom('');
                  setDateTo('');
                }}
                className={`px-3 py-1 rounded-lg text-[11px] font-semibold border transition-colors ${
                  filterPeriod === value && !hasCustomDate
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'bg-slate-50 dark:bg-slate-950 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Séparateur */}
          <div className="hidden sm:flex items-center text-slate-300 dark:text-slate-700">|</div>

          {/* Filtre date personnalisé */}
          <div className="flex items-center gap-2 flex-wrap">
            <CalendarDays className="h-3.5 w-3.5 text-slate-400 shrink-0" />
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value);
                setFilterPeriod('all'); // désactiver les raccourcis
              }}
              className="text-[11px] px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              title="Date de début"
            />
            <span className="text-[11px] text-slate-400">→</span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value);
                setFilterPeriod('all');
              }}
              className="text-[11px] px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              title="Date de fin"
            />
          </div>
        </div>

        {/* Compteur */}
        <p className="text-[11px] text-slate-400">
          {filteredEntries.length} analyse{filteredEntries.length !== 1 ? 's' : ''} affichée{filteredEntries.length !== 1 ? 's' : ''}
          {entries.length !== filteredEntries.length && ` sur ${entries.length}`}
        </p>
      </div>

      {/* ── Résultat de comparaison ── */}
      {comparisonResult && (
        <div className="rounded-2xl border border-indigo-200 dark:border-indigo-800 overflow-hidden shadow-sm">
          {/* Bandeau du comparatif */}
          <div className="flex items-center justify-between px-5 py-3 bg-indigo-600 text-white">
            <div className="flex items-center gap-2">
              <GitCompare className="h-4 w-4 opacity-80" />
              <span className="text-sm font-bold">Résultat du Comparatif Temporel</span>
              <span className="text-xs opacity-70 font-normal">
                {comparisonResult.periods_count
                  ? `${comparisonResult.periods_count} périodes comparées`
                  : ''}
              </span>
            </div>
            <button
              onClick={() => {
                setComparisonResult(null);
                setSelectedIds([]);
              }}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/15 hover:bg-white/25 text-white text-xs font-semibold transition-colors"
            >
              <X className="h-3.5 w-3.5" />
              Fermer le comparatif
            </button>
          </div>

          <div className="p-4 space-y-4">
            {comparisonResult.steps && comparisonResult.steps.length > 0 ? (
              comparisonResult.steps.map((step, idx) => (
                <PeriodComparisonPanel key={idx} report={step.report} />
              ))
            ) : (
              <PeriodComparisonPanel report={comparisonResult} />
            )}
          </div>
        </div>
      )}

      {/* ── Liste des analyses ── */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-indigo-600" />
          <p className="text-xs">Chargement de l'historique partagé...</p>
        </div>
      ) : filteredEntries.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
          <Database className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            Aucune analyse correspondant aux filtres
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Modifiez les filtres ou lancez une nouvelle analyse.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredEntries.map((e) => {
            const isSelected = selectedIds.includes(e.id);
            const open = openId === e.id;

            return (
              <div
                key={e.id}
                className={`bg-white dark:bg-slate-900 border rounded-2xl transition-all shadow-xs overflow-hidden ${
                  isSelected
                    ? 'border-indigo-500 dark:border-indigo-500 ring-2 ring-indigo-500/20'
                    : 'border-slate-200 dark:border-slate-800'
                }`}
              >
                <div className="p-4 flex items-center gap-3">
                  {/* Checkbox sélection comparaison */}
                  <button
                    onClick={() => toggleSelect(e.id)}
                    title={isSelected ? 'Désélectionner' : 'Sélectionner pour comparaison'}
                    className="p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                  >
                    {isSelected ? (
                      <CheckSquare className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                    ) : (
                      <Square className="h-4 w-4 text-slate-300 dark:text-slate-600" />
                    )}
                  </button>

                  {/* Infos principales */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                        {e.title}
                      </p>
                      {/* Badge Opérateur (nom d'utilisateur admin) */}
                      <span className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                        <User className="h-3 w-3" />
                        <strong>{e.operator_username}</strong>
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                      {fmtDate(e.savedAt)}
                      {typeof e.rows === 'number' && ` · ${e.rows.toLocaleString('fr-FR')} ligne${e.rows > 1 ? 's' : ''}`}
                      {e.isDb && (
                        <span className="ml-1.5 text-emerald-600 dark:text-emerald-400 text-[10px]">· BD</span>
                      )}
                    </p>
                  </div>

                  {/* Bouton déplier */}
                  {e.report && (
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
                          Détails
                        </>
                      )}
                    </button>
                  )}
                </div>

                {/* Vue détaillée */}
                {open && e.report && (
                  <div className="border-t border-slate-200 dark:border-slate-800 p-4 space-y-6 bg-slate-50/50 dark:bg-slate-950/30">
                    {e.kind === 'multi' ? (
                      <>
                        <ConsolidatedPanel res={e.report} />
                        {Object.keys(e.report?.results || {}).map((slug) => (
                          <BiReport
                            key={slug}
                            report={{
                              label: `${e.title} / ${slug}`,
                              results: e.report.results[slug] || {},
                              insights: e.report.insights?.[slug] || [],
                              row_count: e.rows || 0,
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
