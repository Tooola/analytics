import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Zap, 
  Layers, 
  Database, 
  Settings, 
  Server, 
  Sun,
  Moon,
  LogOut,
  UserRound,
  Clock
} from 'lucide-react';
import { api, getApiBase, setApiBase } from '../api/client';
import { useTheme } from '../context/ThemeContext';

export default function Navbar({ activeTab, setActiveTab, user, onLogout }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [apiUrlInput, setApiUrlInput] = useState(getApiBase());
  const { theme, toggleTheme } = useTheme();

  const checkStatus = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSaveUrl = (e) => {
    e.preventDefault();
    setApiBase(apiUrlInput);
    setIsConfigOpen(false);
    setLoading(true);
    checkStatus();
  };

  // Live status: green = healthy, amber = API reachable but degraded,
  // red = servers unreachable. Derived from the last /health probe.
  const healthState = loading
    ? 'loading'
    : !health
    ? 'offline'
    : health.status === 'healthy' && health.ai_provider
    ? 'online'
    : 'degraded';
  const DOT_STYLES = {
    loading: { bg: 'bg-slate-400', ping: null },
    online: { bg: 'bg-emerald-500', ping: 'bg-emerald-400' },
    degraded: { bg: 'bg-amber-400', ping: 'bg-amber-300' },
    offline: { bg: 'bg-rose-500', ping: 'bg-rose-400' },
  };
  const statusLabel =
    healthState === 'loading'
      ? "Vérification de l'état des services…"
      : healthState === 'online'
      ? `En ligne — IA : ${health.ai_provider} (cliquer pour revérifier)`
      : healthState === 'degraded'
      ? "API joignable mais dégradée (base de données ou IA) — cliquer pour revérifier"
      : 'Serveurs injoignables — cliquer pour revérifier';
  const dot = DOT_STYLES[healthState];

  const navItems = [
    { id: 'overview', label: 'Vue Globale', icon: Activity },
    { id: 'quick-test', label: 'Test Rapide', icon: Zap, highlight: true },
    { id: 'analytics', label: 'Analyse Avancée', icon: Layers },
    { id: 'history', label: 'Historique', icon: Clock },
    { id: 'apps', label: 'Applications & Accès', icon: Database },
  ];

  return (
    <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md sticky top-0 z-40 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <div className="flex items-center space-x-3 cursor-pointer shrink-0" onClick={() => setActiveTab('overview')} title="Open Analytics AI — v1.0.0">
            <div className="h-9 w-9 rounded-xl bg-indigo-50 dark:bg-indigo-600/20 border border-indigo-200 dark:border-indigo-500/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shadow-sm">
              <Activity className="h-5 w-5" />
            </div>
            <div className="whitespace-nowrap">
              <span className="text-base font-bold tracking-tight text-slate-900 dark:text-white">Open Analytics AI</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex flex-nowrap space-x-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                    isActive
                      ? 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-700 shadow-sm'
                      : item.highlight
                      ? 'text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${item.highlight && !isActive ? 'text-indigo-600 dark:text-indigo-400' : ''}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Health Status, Theme Toggle & Target Settings */}
          <div className="flex items-center space-x-2.5 flex-nowrap">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors"
              title={theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
            >
              {theme === 'dark' ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-slate-600" />}
            </button>

            {/* API Endpoint Config button */}
            <button
              onClick={() => setIsConfigOpen(!isConfigOpen)}
              className="flex items-center space-x-1.5 px-2 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs text-slate-700 dark:text-slate-300 transition-colors"
              title="Configurer l'URL du Backend"
            >
              <span className="font-mono text-[11px] max-w-[96px] truncate">{getApiBase().replace(/^https?:\/\//, '')}</span>
              <Settings className="h-3 w-3 text-slate-400" />
            </button>

            {/* Live status dot — green: healthy, amber: API degraded, red: down */}
            <button
              onClick={() => {
                setLoading(true);
                checkStatus();
              }}
              title={statusLabel}
              aria-label={statusLabel}
              className="relative inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors shrink-0"
            >
              <span className="relative flex h-2.5 w-2.5">
                {dot.ping && (
                  <span className={`absolute inline-flex h-full w-full rounded-full ${dot.ping} animate-ping opacity-75`} />
                )}
                <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${dot.bg}`} />
              </span>
            </button>

            {/* Connected operator — avatar circle (end of the bar) */}
            {user && (
              <span
                className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-indigo-50 dark:bg-indigo-600/20 border border-indigo-200 dark:border-indigo-500/30 text-indigo-600 dark:text-indigo-400 shrink-0 select-none"
                title={`Connecté en tant que ${user.username}`}
              >
                <UserRound className="h-4 w-4" />
              </span>
            )}

            {/* Logout — icon only */}
            {user && (
              <button
                onClick={onLogout}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 hover:bg-rose-50 dark:hover:bg-rose-950/40 hover:border-rose-200 dark:hover:border-rose-900/60 hover:text-rose-600 dark:hover:text-rose-400 text-slate-600 dark:text-slate-300 shrink-0 transition-colors"
                title="Se déconnecter"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Endpoint Configuration Modal */}
      {isConfigOpen && (
        <div className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/95 px-4 py-3 shadow-xl transition-colors">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center space-x-2">
              <Server className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <span className="text-slate-700 dark:text-slate-300 font-semibold">Cible API Backend :</span>
              <span className="text-slate-500">Par défaut en local: http://127.0.0.1:8000</span>
            </div>
            <form onSubmit={handleSaveUrl} className="flex items-center space-x-2">
              <input
                type="text"
                value={apiUrlInput}
                onChange={(e) => setApiUrlInput(e.target.value)}
                placeholder="http://127.0.0.1:8000"
                className="px-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono focus:outline-none focus:border-indigo-500 w-72"
              />
              <button
                type="submit"
                className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium transition-colors"
              >
                Appliquer
              </button>
              <button
                type="button"
                onClick={() => {
                  setApiUrlInput('http://127.0.0.1:8000');
                  setApiBase('http://127.0.0.1:8000');
                  setIsConfigOpen(false);
                  checkStatus();
                }}
                className="px-3.5 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg font-medium transition-colors"
              >
                Reset Local
              </button>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
