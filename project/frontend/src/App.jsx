import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import QuickTest from './pages/QuickTest';
import Analytics from './pages/Analytics';
import History from './pages/History';
import AppsManager from './pages/AppsManager';
import UsersManager from './pages/UsersManager';
import Login from './pages/Login';
import { ThemeProvider } from './context/ThemeContext';
import { LanguageProvider, useLanguage } from './i18n/LanguageContext';
import { api, getAuthToken, clearAuthToken } from './api/client';

function AppContent() {
  const [activeTab, setActiveTab] = useState('quick-test');
  const [authed, setAuthed] = useState(() => !!getAuthToken());
  const [user, setUser] = useState(null);
  const { t } = useLanguage();

  useEffect(() => {
    const onUnauthorized = () => {
      clearAuthToken();
      setAuthed(false);
      setUser(null);
    };
    window.addEventListener('oak:unauthorized', onUnauthorized);
    return () => window.removeEventListener('oak:unauthorized', onUnauthorized);
  }, []);

  useEffect(() => {
    if (!authed) return;
    let cancelled = false;
    api
      .me()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [authed]);

  const handleLogin = (me) => {
    setAuthed(true);
    setUser(me);
  };

  const handleLogout = () => {
    clearAuthToken();
    setAuthed(false);
    setUser(null);
    setActiveTab('quick-test');
  };

  return !authed ? (
    <Login onLogin={handleLogin} />
  ) : (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white transition-colors">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} user={user} onLogout={handleLogout} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <Overview setActiveTab={setActiveTab} />}
        {activeTab === 'quick-test' && <QuickTest currentUser={user} />}
        {activeTab === 'analytics' && <Analytics currentUser={user} />}
        {activeTab === 'history' && <History currentUser={user} />}
        {activeTab === 'apps' && <AppsManager />}
        {activeTab === 'users' && <UsersManager currentUser={user} />}
      </main>
      <footer className="border-t border-slate-200 dark:border-slate-900 bg-white/80 dark:bg-slate-950/80 py-6 text-center text-xs text-slate-500 font-mono transition-colors">
        <p>{t('footer.text', "Open Analytics AI • Moteur Centralisé d'Analyses Décisionnelles • Production Ready")}</p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </ThemeProvider>
  );
}
