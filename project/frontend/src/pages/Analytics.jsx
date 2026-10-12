import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Play, 
  Key, 
  Database, 
  AlertCircle, 
  FileCode,
  SlidersHorizontal
} from 'lucide-react';
import { api, getStoredApiKey, setStoredApiKey } from '../api/client';
import BiReport from '../components/BiReport';

export default function Analytics() {
  const [apps, setApps] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [selectedApp, setSelectedApp] = useState('');
  const [selectedDs, setSelectedDs] = useState('');
  const [apiKey, setApiKey] = useState(getStoredApiKey());
  const [dataText, setDataText] = useState('[\n  {"valeur": 120, "score": 4.5},\n  {"valeur": 140, "score": 4.8}\n]');
  const [analyses, setAnalyses] = useState(['summary', 'trend', 'anomaly']);
  const [includeAi, setIncludeAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);

  useEffect(() => {
    async function init() {
      try {
        const [aData, dData] = await Promise.all([
          api.getApplications().catch(() => []),
          api.getDatasets().catch(() => []),
        ]);
        setApps(aData);
        setDatasets(dData);
        if (aData.length > 0) setSelectedApp(aData[0].slug);
      } catch (e) {
        console.error(e);
      }
    }
    init();
  }, []);

  const filteredDatasets = datasets.filter(d => d.application_slug === selectedApp || !selectedApp);

  const handleRun = async () => {
    setError(null);
    if (!selectedApp) {
      setError('Veuillez sélectionner une application.');
      return;
    }
    if (!selectedDs) {
      setError('Veuillez sélectionner un dataset.');
      return;
    }
    if (!apiKey) {
      setError('Veuillez fournir la clé API correspondant à cette application.');
      return;
    }

    let parsedData = null;
    try {
      parsedData = JSON.parse(dataText);
      if (!Array.isArray(parsedData) || parsedData.length === 0) {
        throw new Error('Les données doivent être un tableau d\'objets non-vide.');
      }
    } catch (e) {
      setError(`JSON invalide : ${e.message}`);
      return;
    }

    setStoredApiKey(apiKey);
    setLoading(true);

    try {
      const res = await api.analyze({
        application: selectedApp,
        dataset: selectedDs,
        analysis: analyses,
        data: parsedData,
        include_ai: includeAi,
        apiKey: apiKey,
      });

      if (!res.success) {
        throw new Error(res.error || 'Échec de la validation du schéma de données.');
      }

      setReport({
        ...res,
        label: `${selectedApp} / ${selectedDs}`,
      });
    } catch (err) {
      setError(err.message || "Erreur lors de l'exécution de l'analyse.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with high contrast in both light and dark mode */}
      <div>
        <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 text-xs font-mono uppercase tracking-wider">
          <Layers className="h-4 w-4" />
          <span>Pipeline Formel Sécurisé</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Exécution d'Analyse avec Schéma & Clé API</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Appel sécurisé validant les données entrantes par rapport aux types déclarés dans la base de données.
        </p>
      </div>

      {/* Selectors Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 transition-colors">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1.5 uppercase tracking-wider">Application</label>
            <select
              value={selectedApp}
              onChange={(e) => {
                setSelectedApp(e.target.value);
                setSelectedDs('');
              }}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 font-medium"
            >
              <option value="">Sélectionnez une application...</option>
              {apps.map((a) => (
                <option key={a.id} value={a.slug}>{a.name} ({a.slug})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1.5 uppercase tracking-wider">Dataset Déclaré</label>
            <select
              value={selectedDs}
              onChange={(e) => setSelectedDs(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 font-medium"
            >
              <option value="">Sélectionnez un dataset...</option>
              {filteredDatasets.map((d) => (
                <option key={d.id} value={d.slug}>{d.name} ({d.slug})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1.5 uppercase tracking-wider">Clé API (Header X-API-Key)</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="anal_..."
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs text-slate-700 dark:text-slate-300 font-semibold mb-1.5 uppercase tracking-wider">Données JSON</label>
          <textarea
            value={dataText}
            onChange={(e) => setDataText(e.target.value)}
            rows={6}
            className="w-full p-3 bg-slate-50 dark:bg-slate-950 font-mono text-xs text-emerald-700 dark:text-emerald-300 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:border-indigo-500 resize-none leading-relaxed"
          />
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-xs text-rose-700 dark:text-rose-300 flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-rose-600 dark:text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            onClick={handleRun}
            disabled={loading}
            className="py-2.5 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors flex items-center space-x-2 shadow-md shadow-indigo-600/20"
          >
            {loading ? (
              <span>Calcul en cours...</span>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Exécuter l'Analyse</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Report Render */}
      {report && (
        <div className="pt-4">
          <BiReport report={report} rawData={JSON.parse(dataText || '[]')} />
        </div>
      )}
    </div>
  );
}
