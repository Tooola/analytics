import React, { useState } from 'react';
import { 
  Zap, 
  Play, 
  FileCode, 
  Sparkles, 
  AlertCircle, 
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react';
import { api } from '../api/client';
import { saveHistory } from '../api/history';
import BiReport from '../components/BiReport';

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

export default function QuickTest() {
  const [jsonText, setJsonText] = useState(JSON.stringify(SAMPLE_FARMTINZ, null, 2));
  const [label, setLabel] = useState('Farmtinz Harvest');
  const [includeAi, setIncludeAi] = useState(true);
  const [analyses, setAnalyses] = useState(['summary', 'trend', 'anomaly', 'correlation', 'forecast']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [parsedData, setParsedData] = useState(SAMPLE_FARMTINZ);

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
      // Saved to the local history so leaving the page never loses a run.
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

  const toggleAnalysis = (type) => {
    if (analyses.includes(type)) {
      setAnalyses(analyses.filter(a => a !== type));
    } else {
      setAnalyses([...analyses, type]);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div>
        <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 text-xs font-mono uppercase tracking-wider">
          <Zap className="h-4 w-4" />
          <span>Test Instantané sans Déclaration Préalable</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Banc d'Essai Rapide</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
          Collez votre tableau JSON. Les colonnes et métriques sont déduites automatiquement par le moteur pour générer instantanément visualisations et recommandations.
        </p>
      </div>

      {/* Editor & Controls Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: JSON Editor */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 flex flex-col shadow-sm transition-colors">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 text-xs">
            <div className="flex items-center space-x-2 text-slate-700 dark:text-slate-300 font-semibold">
              <FileCode className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <span>Données JSON ({parsedData.length} lignes chargées)</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={() => {
                  setJsonText(JSON.stringify(SAMPLE_FARMTINZ, null, 2));
                  setParsedData(SAMPLE_FARMTINZ);
                  setLabel('Farmtinz Harvest');
                }}
                className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
              >
                Exemple Agricole
              </button>
              <button
                type="button"
                onClick={() => {
                  setJsonText(JSON.stringify(SAMPLE_ECOMMERCE, null, 2));
                  setParsedData(SAMPLE_ECOMMERCE);
                  setLabel('E-Commerce KPI');
                }}
                className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
              >
                Exemple Ventes
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
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                Analyses à Conduire
              </label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {['summary', 'trend', 'anomaly', 'correlation', 'distribution', 'forecast'].map((mod) => (
                  <button
                    key={mod}
                    type="button"
                    onClick={() => toggleAnalysis(mod)}
                    className={`px-3 py-2 rounded-xl border text-left font-medium capitalize transition-all ${
                      analyses.includes(mod)
                        ? 'bg-indigo-50 dark:bg-indigo-600/20 border-indigo-300 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300'
                        : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                    }`}
                  >
                    {mod}
                  </button>
                ))}
              </div>
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
                  <span className="text-xs font-semibold text-slate-900 dark:text-white block">Avis Exécutif IA (Groq Cloud)</span>
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

      {/* Results View */}
      {report && (
        <div className="pt-4">
          <BiReport report={report} rawData={parsedData} />
        </div>
      )}
    </div>
  );
}
