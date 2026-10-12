import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import QuickTest from './pages/QuickTest';
import Analytics from './pages/Analytics';
import AppsManager from './pages/AppsManager';
import { ThemeProvider } from './context/ThemeContext';

export default function App() {
  const [activeTab, setActiveTab] = useState('quick-test');

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white transition-colors">
        {/* Top Navbar */}
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

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
    </ThemeProvider>
  );
}
