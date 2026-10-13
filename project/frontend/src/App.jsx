import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import QuickTest from './pages/QuickTest';
import Analytics from './pages/Analytics';
import AppsManager from './pages/AppsManager';
import Login from './pages/Login';
import { ThemeProvider } from './context/ThemeContext';
import { api, getAuthToken, clearAuthToken } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('quick-test');
  // Session exists if a JWT is stored; validated against /auth/me below.
  const [authed, setAuthed] = useState(() => !!getAuthToken());
  const [user, setUser] = useState(null);

  // Token expired / revoked while using the app → back to login.
  useEffect(() => {
    const onUnauthorized = () => {
      clearAuthToken();
      setAuthed(false);
      setUser(null);
    };
    window.addEventListener('oak:unauthorized', onUnauthorized);
    return () => window.removeEventListener('oak:unauthorized', onUnauthorized);
  }, []);

  // Resolve the connected user when a stored token exists.
  useEffect(() => {
    if (!authed) return;
    let cancelled = false;
    api
      .me()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        // 401 triggers the unauthorized event; other errors leave user null.
      });
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

  return (
    <ThemeProvider>
      {!authed ? (
        <Login onLogin={handleLogin} />
      ) : (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white transition-colors">
          {/* Top Navbar */}
          <Navbar activeTab={activeTab} setActiveTab={setActiveTab} user={user} onLogout={handleLogout} />

          {/* Main Container */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {activeTab === 'overview' && <Overview setActiveTab={setActiveTab} />}
            {activeTab === 'quick-test' && <QuickTest />}
            {activeTab === 'analytics' && <Analytics />}
            {activeTab === 'apps' && <AppsManager />}
          </main>

          {/* Footer */}
          <footer className="border-t border-slate-200 dark:border-slate-900 bg-white/80 dark:bg-slate-950/80 py-6 text-center text-xs text-slate-500 font-mono transition-colors">
            <p>Open Analytics AI • Moteur Centralisé d'Analyses Décisionnelles • Production Ready</p>
          </footer>
        </div>
      )}
    </ThemeProvider>
  );
}
