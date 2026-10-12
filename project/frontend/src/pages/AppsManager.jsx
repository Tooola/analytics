import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Key, 
  Plus, 
  Copy, 
  Check, 
  RefreshCw, 
  Layers, 
  Trash2,
  AlertCircle
} from 'lucide-react';
import { api, setStoredApiKey } from '../api/client';
import Modal from '../components/Modal';

export default function AppsManager() {
  const [apps, setApps] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copiedKey, setCopiedKey] = useState(null);
  const [newAppName, setNewAppName] = useState('');
  const [newAppDesc, setNewAppDesc] = useState('');
  const [createdKey, setCreatedKey] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Modal states
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    title: '',
    message: '',
    type: 'info',
    onConfirm: null,
    confirmText: 'Confirmer',
  });

  const closeModal = () => {
    setModalConfig(prev => ({ ...prev, isOpen: false }));
  };

  const showInfoModal = (title, message, type = 'info') => {
    setModalConfig({
      isOpen: true,
      title,
      message,
      type,
      onConfirm: null,
    });
  };

  const showConfirmModal = (title, message, onConfirm, type = 'danger', confirmText = 'Supprimer') => {
    setModalConfig({
      isOpen: true,
      title,
      message,
      type,
      onConfirm: () => {
        closeModal();
        onConfirm();
      },
      confirmText,
    });
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [aData, dData] = await Promise.all([
        api.getApplications().catch(() => []),
        api.getDatasets().catch(() => []),
      ]);
      setApps(Array.isArray(aData) ? aData : []);
      setDatasets(Array.isArray(dData) ? dData : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateApp = async (e) => {
    e.preventDefault();
    if (!newAppName.trim()) return;
    setSubmitting(true);
    try {
      const result = await api.createApplication({
        name: newAppName.trim(),
        description: newAppDesc.trim(),
      });
      if (result.api_key) {
        setCreatedKey({ name: newAppName, key: result.api_key });
        setStoredApiKey(result.api_key);
      }
      setNewAppName('');
      setNewAppDesc('');
      await loadData();
      showInfoModal('Succès', `L'application ${result.name} a été enregistrée avec succès.`, 'success');
    } catch (err) {
      showInfoModal('Erreur de création', err.message || "Impossible d'enregistrer l'application.", 'danger');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteApp = (app) => {
    showConfirmModal(
      'Confirmation de suppression',
      `Êtes-vous certain de vouloir supprimer l'application "${app.name}" ? Toutes les clés et datasets associés seront supprimés.`,
      async () => {
        try {
          await api.deleteApplication(app.id);
          await loadData();
          showInfoModal('Supprimé', `L'application ${app.name} a été supprimée.`, 'info');
        } catch (err) {
          showInfoModal('Erreur', err.message, 'danger');
        }
      },
      'danger',
      'Confirmer la suppression'
    );
  };

  const handleRegenerateKey = (app) => {
    showConfirmModal(
      'Renouvellement de clé API',
      `Voulez-vous générer une nouvelle clé pour "${app.name}" ? L'ancienne clé sera immédiatement révoquée.`,
      async () => {
        try {
          const res = await api.regenerateApiKey(app.id);
          if (res.api_key) {
            setCreatedKey({ name: app.name, key: res.api_key });
            setStoredApiKey(res.api_key);
            showInfoModal('Clé Régénérée', `Une nouvelle clé d'accès a été générée pour ${app.name}.`, 'success');
          }
        } catch (err) {
          showInfoModal('Erreur', err.message, 'danger');
        }
      },
      'info',
      'Générer la nouvelle clé'
    );
  };

  const handleCopy = (key) => {
    navigator.clipboard.writeText(key);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Custom Tailwind Modal */}
      <Modal
        isOpen={modalConfig.isOpen}
        onClose={closeModal}
        onConfirm={modalConfig.onConfirm}
        title={modalConfig.title}
        message={modalConfig.message}
        type={modalConfig.type}
        confirmText={modalConfig.confirmText}
      />

      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 text-xs font-mono uppercase tracking-wider">
          <Database className="h-4 w-4" />
          <span>Registre des Applications & Clés d'Accès</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Applications & Datasets Déclarés</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Chaque application cliente (Farmtinz, CRMtinz, Sharetinz) possède sa clé API isolée.
        </p>
      </div>

      {/* Created Key Banner */}
      {createdKey && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 flex items-center justify-between text-xs transition-colors">
          <div>
            <span className="font-bold text-emerald-800 dark:text-emerald-300 block">Nouvelle Clé API Générée pour {createdKey.name}</span>
            <span className="text-slate-700 dark:text-slate-300 font-mono mt-1 block select-all">{createdKey.key}</span>
            <span className="text-[11px] text-amber-700 dark:text-amber-400 mt-1 block">Conservez cette clé, elle ne sera plus affichée en clair.</span>
          </div>
          <button
            onClick={() => handleCopy(createdKey.key)}
            className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center space-x-1.5 shrink-0 shadow-sm"
          >
            {copiedKey === createdKey.key ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
            <span>Copier la clé</span>
          </button>
        </div>
      )}

      {/* Applications List & Creation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Apps List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center">
            <Key className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
            Applications Enregistrées ({apps.length})
          </h2>

          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
              Chargement des applications...
            </div>
          ) : apps.length === 0 ? (
            <div className="p-8 rounded-2xl bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500 dark:text-slate-400">
              Aucune application enregistrée pour le moment.
            </div>
          ) : (
            <div className="space-y-3">
              {apps.map((app) => (
                <div key={app.id} className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-between shadow-sm transition-colors">
                  <div>
                    <div className="flex items-center space-x-2.5">
                      <span className="font-bold text-slate-900 dark:text-white text-sm">{app.name}</span>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                        {app.slug}
                      </span>
                    </div>
                    {app.description && <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{app.description}</p>}
                    <div className="flex items-center space-x-4 mt-2 text-[11px] font-mono text-slate-400 dark:text-slate-500">
                      <span>ID: {app.id ? app.id.slice(0, 8) : ''}...</span>
                      <span>Créé le: {app.created_at ? new Date(app.created_at).toLocaleDateString() : 'N/A'}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleRegenerateKey(app)}
                      className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs transition-colors"
                      title="Régénérer une nouvelle clé API"
                    >
                      <RefreshCw className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDeleteApp(app)}
                      className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/60 text-rose-600 dark:text-rose-400 text-xs transition-colors"
                      title="Supprimer cette application"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create App Form */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 h-fit shadow-sm transition-colors">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4 flex items-center">
            <Plus className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
            Déclarer une Application
          </h3>

          <form onSubmit={handleCreateApp} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Nom de l'application</label>
              <input
                type="text"
                value={newAppName}
                onChange={(e) => setNewAppName(e.target.value)}
                placeholder="Ex: Farmtinz Production"
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Description (optionnelle)</label>
              <textarea
                value={newAppDesc}
                onChange={(e) => setNewAppDesc(e.target.value)}
                rows={3}
                placeholder="Ex: Système de gestion des récoltes et ventes agricoles"
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={submitting || !newAppName.trim()}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors disabled:bg-slate-200 dark:disabled:bg-slate-800 disabled:text-slate-400"
            >
              {submitting ? 'Création en cours...' : 'Créer & Générer Clé API'}
            </button>
          </form>
        </div>
      </div>

      {/* Datasets List */}
      <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center">
          <Layers className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
          Jeux de Données Déclarés ({datasets.length})
        </h2>

        {datasets.length === 0 ? (
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400">
            Aucun schéma de dataset formel déclaré. (L'endpoint <strong>Test Rapide</strong> permet de tester directement n'importe quel tableau JSON sans déclaration).
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {datasets.map((ds) => (
              <div key={ds.id} className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 dark:text-white text-xs">{ds.name}</span>
                  <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                    {ds.slug}
                  </span>
                </div>
                <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  <span>Application: </span>
                  <span className="text-indigo-600 dark:text-indigo-400 font-medium">{ds.application_slug || ds.application_id}</span>
                </div>
                {ds.fields && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {ds.fields.map((f, fIdx) => (
                      <span key={fIdx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-950 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800">
                        {f.name} ({f.technical_type})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
