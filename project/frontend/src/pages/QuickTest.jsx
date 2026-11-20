import React, { useState } from 'react';
import { 
  Zap, 
  Play, 
  FileCode, 
  Sparkles, 
  AlertCircle, 
  SlidersHorizontal,
  GitCompare,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { saveHistory } from '../api/history';
import BiReport from '../components/BiReport';
import PeriodComparisonPanel from '../components/PeriodComparisonPanel';

const SAMPLE_FARMTINZ = [
  { "date": "2026-09-01", "culture": "Maïs", "rendement_kg": 4500, "pluviometrie_mm": 42.5, "temperature_c": 24.1 },
  { "date": "2026-09-02", "culture": "Blé",  "rendement_kg": 3200, "pluviometrie_mm": 18.0, "temperature_c": 22.8 },
  { "date": "2026-09-03", "culture": "Soja",  "rendement_kg": 5100, "pluviometrie_mm": 55.2, "temperature_c": 25.0 },
  { "date": "2026-09-04", "culture": "Maïs", "rendement_kg": 4650, "pluviometrie_mm": 38.0, "temperature_c": 23.5 },
  { "date": "2026-09-05", "culture": "Tournesol", "rendement_kg": 2800, "pluviometrie_mm": 12.4, "temperature_c": 26.2 },
  { "date": "2026-09-06", "culture": "Blé",  "rendement_kg": 3400, "pluviometrie_mm": 22.1, "temperature_c": 23.1 },
  { "date": "2026-09-07", "culture": "Soja",  "rendement_kg": 13500, "pluviometrie_mm": 90.0, "temperature_c": 27.5 },
  { "date": "2026-09-08", "culture": "Maïs", "rendement_kg": 4800, "pluviometrie_mm": 44.0, "temperature_c": 24.0 }
];

const SAMPLE_ECOMMERCE = [
  { "date": "2026-10-01", "ventes_unites": 120, "panier_moyen": 48.5, "depenses_marketing": 500, "visiteurs": 3200 },
  { "date": "2026-10-02", "ventes_unites": 135, "panier_moyen": 51.0, "depenses_marketing": 520, "visiteurs": 3400 },
  { "date": "2026-10-03", "ventes_unites": 140, "panier_moyen": 49.2, "depenses_marketing": 510, "visiteurs": 3350 },
  { "date": "2026-10-04", "ventes_unites": 290, "panier_moyen": 78.0, "depenses_marketing": 1200, "visiteurs": 7100 },
  { "date": "2026-10-05", "ventes_unites": 145, "panier_moyen": 52.1, "depenses_marketing": 540, "visiteurs": 3600 },
  { "date": "2026-10-06", "ventes_unites": 160, "panier_moyen": 54.0, "depenses_marketing": 580, "visiteurs": 3900 }
];

const SAMPLE_DEMOGRAPHIE = [
  { "region": "Île-de-France", "population": 12278210, "taux_chomage_pct": 6.8, "age_median": 35.8, "revenu_median_eur": 28450 },
  { "region": "Auvergne-Rhône-Alpes", "population": 8078652, "taux_chomage_pct": 6.2, "age_median": 41.2, "revenu_median_eur": 24200 },
  { "region": "Nouvelle-Aquitaine", "population": 6032900, "taux_chomage_pct": 6.9, "age_median": 44.5, "revenu_median_eur": 22100 },
  { "region": "Occitanie", "population": 5973969, "taux_chomage_pct": 8.7, "age_median": 43.1, "revenu_median_eur": 21800 },
  { "region": "Hauts-de-France", "population": 5997495, "taux_chomage_pct": 9.2, "age_median": 39.4, "revenu_median_eur": 20900 },
  { "region": "Grand Est", "population": 5562651, "taux_chomage_pct": 7.4, "age_median": 42.0, "revenu_median_eur": 22600 },
  { "region": "Provence-Alpes-Côte d'Azur", "population": 5098666, "taux_chomage_pct": 8.1, "age_median": 43.8, "revenu_median_eur": 23400 },
  { "region": "Bretagne", "population": 3373835, "taux_chomage_pct": 5.9, "age_median": 43.6, "revenu_median_eur": 23100 }
];

// Presets for Period Comparison (e.g. Month M-1 vs Month M)
const SAMPLE_COMPARE_A = [
  { "date": "2026-10-01", "ventes_unites": 120, "chiffre_affaires_eur": 12000, "depenses_marketing_eur": 1500, "visiteurs": 3200, "taux_retours_pct": 3.2 },
  { "date": "2026-10-02", "ventes_unites": 135, "chiffre_affaires_eur": 13500, "depenses_marketing_eur": 1550, "visiteurs": 3400, "taux_retours_pct": 3.1 },
  { "date": "2026-10-03", "ventes_unites": 140, "chiffre_affaires_eur": 14000, "depenses_marketing_eur": 1520, "visiteurs": 3350, "taux_retours_pct": 3.4 },
  { "date": "2026-10-04", "ventes_unites": 130, "chiffre_affaires_eur": 13000, "depenses_marketing_eur": 1480, "visiteurs": 3300, "taux_retours_pct": 3.0 },
  { "date": "2026-10-05", "ventes_unites": 145, "chiffre_affaires_eur": 14500, "depenses_marketing_eur": 1600, "visiteurs": 3600, "taux_retours_pct": 3.3 }
];

const SAMPLE_COMPARE_B = [
  { "date": "2026-11-01", "ventes_unites": 165, "chiffre_affaires_eur": 17200, "depenses_marketing_eur": 1850, "visiteurs": 4100, "taux_retours_pct": 2.8 },
  { "date": "2026-11-02", "ventes_unites": 170, "chiffre_affaires_eur": 17800, "depenses_marketing_eur": 1900, "visiteurs": 4300, "taux_retours_pct": 2.7 },
  { "date": "2026-11-03", "ventes_unites": 180, "chiffre_affaires_eur": 18900, "depenses_marketing_eur": 1880, "visiteurs": 4500, "taux_retours_pct": 2.9 },
  { "date": "2026-11-04", "ventes_unites": 175, "chiffre_affaires_eur": 18200, "depenses_marketing_eur": 1920, "visiteurs": 4400, "taux_retours_pct": 2.6 },
  { "date": "2026-11-05", "ventes_unites": 190, "chiffre_affaires_eur": 19800, "depenses_marketing_eur": 1950, "visiteurs": 4700, "taux_retours_pct": 2.5 }
];

export default function QuickTest() {
  const [activeTab, setActiveTab] = useState('single'); // 'single' | 'compare'

  // Single test state
  const [jsonText, setJsonText] = useState(JSON.stringify(SAMPLE_FARMTINZ, null, 2));
  const [label, setLabel] = useState('Farmtinz Harvest');
  const [includeAi, setIncludeAi] = useState(true);
  const [analyses, setAnalyses] = useState(['auto']);
  const [isManualAnalysis, setIsManualAnalysis] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [parsedData, setParsedData] = useState(SAMPLE_FARMTINZ);

  // Compare test state
  const [compareLabel, setCompareLabel] = useState('Performance Commerciale Mensuelle');
  const [periodALabel, setPeriodALabel] = useState('Mois M-1 (Octobre)');
  const [periodBLabel, setPeriodBLabel] = useState('Mois M (Novembre)');
  const [periodAJson, setPeriodAJson] = useState(JSON.stringify(SAMPLE_COMPARE_A, null, 2));
  const [periodBJson, setPeriodBJson] = useState(JSON.stringify(SAMPLE_COMPARE_B, null, 2));
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState(null);
  const [compareReport, setCompareReport] = useState(null);

  const handleJsonChange = (text) => {
    setJsonText(text);
    setError(null);
    try {
      const parsed = JSON.parse(text);
      if (Array.isArray(parsed)) {
        setParsedData(parsed);
      } else if (typeof parsed === 'object') {
        setParsedData([parsed]);
      }
    } catch {
      // Typing
    }
  };

  const handleRun = async () => {
    setError(null);
    let dataToSubmit = null;

    try {
      const parsed = JSON.parse(jsonText);
      dataToSubmit = Array.isArray(parsed) ? parsed : [parsed];
      if (dataToSubmit.length === 0) {
        throw new Error('Le tableau JSON ne doit pas être vide.');
      }
    } catch (e) {
      setError(`Format JSON invalide : ${e.message}`);
      return;
    }

    setLoading(true);
    try {
      const result = await api.quickAnalyze({
        data: dataToSubmit,
        analysis: analyses,
        include_ai: includeAi,
        label: label || 'quick-test',
      });
      setReport(result);
      setParsedData(dataToSubmit);
      saveHistory({
        kind: 'quick',
        title: label || 'quick-test',
        app: 'Test rapide',
        datasets: [],
        rows: dataToSubmit.length,
        analyses,
        aiStatus: result.ai_status || null,
        report: result,
        payloads: dataToSubmit,
      });
    } catch (err) {
      setError(err.message || "Erreur lors de l'exécution de l'analyse.");
    } finally {
      setLoading(false);
    }
  };

  const handleCompareRun = async () => {
    setCompareError(null);
    let dataA = null;
    let dataB = null;

    try {
      const parsedA = JSON.parse(periodAJson);
      dataA = Array.isArray(parsedA) ? parsedA : [parsedA];
      if (dataA.length === 0) throw new Error('Les données de la Période A sont vides.');
    } catch (e) {
      setCompareError(`Période A invalide : ${e.message}`);
      return;
    }

    try {
      const parsedB = JSON.parse(periodBJson);
      dataB = Array.isArray(parsedB) ? parsedB : [parsedB];
      if (dataB.length === 0) throw new Error('Les données de la Période B sont vides.');
    } catch (e) {
      setCompareError(`Période B invalide : ${e.message}`);
      return;
    }

    setCompareLoading(true);
    try {
      const result = await api.quickCompare({
        period_a: { label: periodALabel || 'Période A', data: dataA },
        period_b: { label: periodBLabel || 'Période B', data: dataB },
        label: compareLabel || 'comparatif-temporel',
        include_ai: includeAi,
      });
      setCompareReport(result);
      saveHistory({
        kind: 'quick',
        title: `Comparatif: ${periodALabel} vs ${periodBLabel}`,
        app: 'Comparatif temporel',
        datasets: [],
        rows: dataA.length + dataB.length,
        analyses: ['compare'],
        aiStatus: result.ai_status || null,
        report: result,
        payloads: { period_a: dataA, period_b: dataB },
      });
    } catch (err) {
      setCompareError(err.message || "Erreur lors de l'exécution du comparatif.");
    } finally {
      setCompareLoading(false);
    }
  };

  const toggleAnalysis = (type) => {
    if (analyses.includes(type)) {
      setAnalyses(analyses.filter(a => a !== type));
    } else {
      setAnalyses([...analyses, type]);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header & Tab Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 text-xs font-mono uppercase tracking-wider">
            <Zap className="h-4 w-4" />
            <span>Test Instantané sans Déclaration Préalable</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Banc d'Essai Rapide</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
            Évaluez vos jeux de données ou comparez deux périodes temporelles (Mois M vs M-1, Année N vs N-1) en un seul clic sans fusion manuelle.
          </p>
        </div>

        {/* Mode Switcher */}
        <div className="flex bg-slate-100 dark:bg-slate-900 p-1.5 rounded-2xl border border-slate-200 dark:border-slate-800 text-xs shrink-0 self-start md:self-auto">
          <button
            onClick={() => setActiveTab('single')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === 'single'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Zap className="h-4 w-4" />
            <span>Analyse Simple</span>
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === 'compare'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <GitCompare className="h-4 w-4" />
            <span>Comparatif Temporel (M vs M-1)</span>
          </button>
        </div>
      </div>

      {/* MODE 1: SINGLE DATASET ANALYSIS */}
      {activeTab === 'single' && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: JSON Editor */}
            <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 flex flex-col shadow-sm transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 text-xs">
                <div className="flex items-center space-x-2 text-slate-700 dark:text-slate-300 font-semibold">
                  <FileCode className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  <span>Données JSON ({parsedData.length} lignes chargées)</span>
                </div>
                <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                  <button
                    type="button"
                    onClick={() => {
                      setJsonText(JSON.stringify(SAMPLE_FARMTINZ, null, 2));
                      setParsedData(SAMPLE_FARMTINZ);
                      setLabel('Farmtinz Harvest');
                    }}
                    className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
                  >
                    Agricole
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setJsonText(JSON.stringify(SAMPLE_ECOMMERCE, null, 2));
                      setParsedData(SAMPLE_ECOMMERCE);
                      setLabel('E-Commerce KPI');
                    }}
                    className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
                  >
                    Ventes
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setJsonText(JSON.stringify(SAMPLE_DEMOGRAPHIE, null, 2));
                      setParsedData(SAMPLE_DEMOGRAPHIE);
                      setLabel('Démographie Régionale');
                    }}
                    className="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/40 font-medium transition-colors"
                  >
                    Démographie
                  </button>
                </div>
              </div>

              <textarea
                value={jsonText}
                onChange={(e) => handleJsonChange(e.target.value)}
                rows={14}
                className="w-full mt-3 p-3 bg-slate-50 dark:bg-slate-950 font-mono text-xs text-emerald-700 dark:text-emerald-300 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:border-indigo-500 resize-none leading-relaxed transition-colors"
                placeholder='[{"colonne": "valeur"}, ...]'
              />

              {error && (
                <div className="mt-3 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-xs text-rose-700 dark:text-rose-300 flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4 text-rose-600 dark:text-rose-400 shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* Right: Configuration */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-sm transition-colors">
              <div className="space-y-5">
                <div className="flex items-center space-x-2 pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300">
                  <SlidersHorizontal className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  <span>Options d'Évaluation</span>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                    Libellé de l'Analyse
                  </label>
                  <input
                    type="text"
                    value={label}
                    onChange={(e) => setLabel(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
                    placeholder="Ex: Évaluation Mensuelle"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                      Sélection des Analyses
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        const next = !isManualAnalysis;
                        setIsManualAnalysis(next);
                        if (!next) setAnalyses(['auto']);
                        else setAnalyses(['summary', 'trend', 'anomaly']);
                      }}
                      className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline"
                    >
                      {isManualAnalysis ? 'Revenir au mode Auto' : 'Personnaliser'}
                    </button>
                  </div>

                  {!isManualAnalysis ? (
                    <div className="p-3 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 text-xs">
                      <div className="flex items-center space-x-2 text-indigo-700 dark:text-indigo-300 font-semibold mb-1">
                        <Sparkles className="h-3.5 w-3.5" />
                        <span>Mode Automatique Intelligent</span>
                      </div>
                      <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                        Le moteur détecte la structure de vos données et applique automatiquement les analyses pertinentes et les moteurs de causalité sans jargon technique.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {[
                        { id: 'summary', label: "Vue d'ensemble" },
                        { id: 'trend', label: "Évolutions" },
                        { id: 'anomaly', label: "Points inhabituels" },
                        { id: 'correlation', label: "Corrélations" },
                        { id: 'distribution', label: "Répartition" },
                        { id: 'forecast', label: "Projections" },
                      ].map(({ id, label: modLabel }) => (
                        <button
                          key={id}
                          type="button"
                          onClick={() => toggleAnalysis(id)}
                          className={`px-3 py-2 rounded-xl border text-left font-medium transition-all ${
                            analyses.includes(id)
                              ? 'bg-indigo-50 dark:bg-indigo-600/20 border-indigo-300 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300'
                              : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                          }`}
                        >
                          {modLabel}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={includeAi}
                      onChange={(e) => setIncludeAi(e.target.checked)}
                      className="h-4 w-4 rounded bg-slate-50 dark:bg-slate-950 border-slate-300 dark:border-slate-700 text-indigo-600 focus:ring-0"
                    />
                    <div>
                      <span className="text-xs font-semibold text-slate-900 dark:text-white block">Avis Exécutif IA</span>
                      <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Synthèse claire pour décideurs sans termes techniques</span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="pt-6">
                <button
                  onClick={handleRun}
                  disabled={loading || analyses.length === 0}
                  className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-400 text-white font-semibold text-xs transition-all shadow-md shadow-indigo-600/20 flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Calcul et génération en cours...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 fill-current" />
                      <span>Lancer l'Évaluation</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {report && (
            <div className="pt-4">
              <BiReport report={report} rawData={parsedData} />
            </div>
          )}
        </>
      )}

      {/* MODE 2: PERIOD COMPARISON (M vs M-1) */}
      {activeTab === 'compare' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Period A Box */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 text-xs">
                <div className="flex items-center space-x-2 text-slate-700 dark:text-slate-300 font-semibold">
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
                  <span>Période de Référence (Période A)</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setPeriodAJson(JSON.stringify(SAMPLE_COMPARE_A, null, 2));
                    setPeriodALabel('Mois M-1 (Octobre)');
                  }}
                  className="px-2 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-[11px] text-slate-600 dark:text-slate-300"
                >
                  Exemple M-1
                </button>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  Nom de la Période A
                </label>
                <input
                  type="text"
                  value={periodALabel}
                  onChange={(e) => setPeriodALabel(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
                  placeholder="Ex: Mois M-1, Octobre, 2025"
                />
              </div>

              <textarea
                value={periodAJson}
                onChange={(e) => setPeriodAJson(e.target.value)}
                rows={10}
                className="w-full p-3 bg-slate-50 dark:bg-slate-950 font-mono text-xs text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:border-indigo-500 resize-none leading-relaxed"
                placeholder='[{"date": "...", "indicateur": 100}, ...]'
              />
            </div>

            {/* Period B Box */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 text-xs">
                <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 font-semibold">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                  <span>Période Récente (Période B)</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setPeriodBJson(JSON.stringify(SAMPLE_COMPARE_B, null, 2));
                    setPeriodBLabel('Mois M (Novembre)');
                  }}
                  className="px-2 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-[11px] text-indigo-600 dark:text-indigo-300"
                >
                  Exemple M
                </button>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  Nom de la Période B
                </label>
                <input
                  type="text"
                  value={periodBLabel}
                  onChange={(e) => setPeriodBLabel(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
                  placeholder="Ex: Mois M, Novembre, 2026"
                />
              </div>

              <textarea
                value={periodBJson}
                onChange={(e) => setPeriodBJson(e.target.value)}
                rows={10}
                className="w-full p-3 bg-slate-50 dark:bg-slate-950 font-mono text-xs text-indigo-700 dark:text-indigo-300 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:border-indigo-500 resize-none leading-relaxed"
                placeholder='[{"date": "...", "indicateur": 130}, ...]'
              />
            </div>
          </div>

          {/* Controls Bar */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center space-x-4 w-full sm:w-auto">
              <input
                type="text"
                value={compareLabel}
                onChange={(e) => setCompareLabel(e.target.value)}
                className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 flex-1 sm:w-72"
                placeholder="Libellé du comparatif"
              />
              <label className="flex items-center space-x-2 cursor-pointer text-xs shrink-0">
                <input
                  type="checkbox"
                  checked={includeAi}
                  onChange={(e) => setIncludeAi(e.target.checked)}
                  className="h-4 w-4 rounded bg-slate-50 dark:bg-slate-950 border-slate-300 dark:border-slate-700 text-indigo-600 focus:ring-0"
                />
                <span className="text-slate-700 dark:text-slate-300 font-medium">Synthèse IA Groq</span>
              </label>
            </div>

            <button
              onClick={handleCompareRun}
              disabled={compareLoading}
              className="w-full sm:w-auto py-2.5 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-400 text-white font-semibold text-xs transition-all shadow-md shadow-indigo-600/20 flex items-center justify-center space-x-2"
            >
              {compareLoading ? (
                <>
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Comparaison en cours...</span>
                </>
              ) : (
                <>
                  <GitCompare className="h-4 w-4" />
                  <span>Lancer le Comparatif Temporel</span>
                </>
              )}
            </button>
          </div>

          {compareError && (
            <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-xs text-rose-700 dark:text-rose-300 flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-rose-600 dark:text-rose-400 shrink-0" />
              <span>{compareError}</span>
            </div>
          )}

          {/* Results: Period Comparison Panel */}
          {compareReport && (
            <div className="pt-2">
              <PeriodComparisonPanel report={compareReport} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
