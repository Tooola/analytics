import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Server, 
  Database, 
  Cpu, 
  CheckCircle2, 
  Zap, 
  Layers, 
  Key, 
  ShieldCheck, 
  Code2
} from 'lucide-react';
import { api, getApiBase } from '../api/client';
import KpiCard from '../components/KpiCard';

export default function Overview({ setActiveTab }) {
  const [health, setHealth] = useState(null);
  const [apps, setApps] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [hData, aData, dData] = await Promise.all([
          api.getHealth().catch(() => null),
          api.getApplications().catch(() => []),
          api.getDatasets().catch(() => []),
        ]);
        setHealth(hData);
        setApps(Array.isArray(aData) ? aData : []);
        setDatasets(Array.isArray(dData) ? dData : []);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Welcome */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-200 dark:border-slate-800 p-8 shadow-xl text-white">
        <div className="max-w-2xl">
          <div className="flex items-center space-x-2 text-indigo-400 text-xs font-mono uppercase tracking-wider mb-2">
            <Activity className="h-4 w-4" />
            <span>Moteur d'Intelligence Décisionnelle</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">
            Plateforme Analytics & Décision
          </h1>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Moteur de calculs statistiques robustes (détection de signaux faibles, tendances, variations)
            et d'orientations stratégiques claires pour les dirigeants d'entreprise.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => setActiveTab('quick-test')}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors flex items-center space-x-2 shadow-lg shadow-indigo-950/50"
            >
              <Zap className="h-4 w-4" />
              <span>Tester immédiatement avec du JSON</span>
            </button>
            <button
              onClick={() => setActiveTab('apps')}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-colors flex items-center space-x-2 border border-slate-700"
            >
              <Key className="h-4 w-4 text-slate-400" />
              <span>Gérer les Applications & Clés d'Accès</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard
          title="Statut Moteur"
          value={health?.status === 'healthy' ? 'Opérationnel' : 'Hors ligne'}
          subtext={`Backend sur ${getApiBase().replace(/^https?:\/\//, '')}`}
          icon={Server}
          color={health?.status === 'healthy' ? 'emerald' : 'rose'}
        />
        <KpiCard
          title="Base de Données"
          value={health?.database === 'connected' ? 'Connectée' : 'Déconnectée'}
          subtext="Persistance des métadonnées"
          icon={Database}
          color={health?.database === 'connected' ? 'sky' : 'rose'}
        />
        <KpiCard
          title="Générateur d'Avis IA"
          value={health?.ai_provider || 'Non configuré'}
          subtext="Analyse stratégique"
          icon={Cpu}
          color="indigo"
        />
        <KpiCard
          title="Applications Connectées"
          value={apps.length}
          subtext={`${datasets.length} datasets déclarés`}
          icon={Layers}
          color="amber"
        />
      </div>

      {/* Architecture & Specs Block */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Specifications */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm transition-colors">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center">
            <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mr-2" />
            Engagements de Qualité & Confidentialité
          </h3>
          <div className="space-y-3.5 text-xs">
            <div className="flex items-start space-x-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-900 dark:text-white block">Fiabilité des Calculs</span>
                <span className="text-slate-600 dark:text-slate-400">Tri sélectif des valeurs atypiques par consensus croisé, analyse des variations réelles sans extrapolation fantaisiste.</span>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-900 dark:text-white block">Confidentialité Totale</span>
                <span className="text-slate-600 dark:text-slate-400">Vos enregistrements nominatifs ne sont jamais transmis aux modèles de langage. Seules les synthèses chiffrées anonymisées sont traitées.</span>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-900 dark:text-white block">Intégration Standardisée</span>
                <span className="text-slate-600 dark:text-slate-400">Une interface API REST universelle pour relier facilement vos systèmes web, mobiles ou métiers.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Integration Quick Guide */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm transition-colors">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center">
            <Code2 className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
            Exemple d'Appel API (JavaScript)
          </h3>
          <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto leading-relaxed">
            <pre>{`const response = await fetch("${getApiBase()}/api/v1/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "anal_votre_cle_api"
  },
  body: JSON.stringify({
    application: "farmtinz",
    dataset: "recolte-2026",
    analysis: ["summary", "trend", "anomaly"],
    data: [ { culture: "Maïs", quantite_kg: 4500 } ],
    include_ai: true
  })
});
const result = await response.json();`}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
