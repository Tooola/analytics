import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import fr from './translations/fr.json';
import en from './translations/en.json';

const translations = { fr, en };

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('oak_lang') || 'fr';
  });

  useEffect(() => {
    localStorage.setItem('oak_lang', language);
    document.documentElement.lang = language;
  }, [language]);

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'fr' ? 'en' : 'fr'));
  };

  const t = useMemo(() => {
    const currentDict = translations[language] || translations.fr;
    const fallbackDict = translations.fr;

    return (path, fallback = '') => {
      const keys = path.split('.');
      let val = currentDict;
      for (const k of keys) {
        if (val && typeof val === 'object' && k in val) {
          val = val[k];
        } else {
          val = undefined;
          break;
        }
      }
      if (val !== undefined && typeof val === 'string') return val;

      let fb = fallbackDict;
      for (const k of keys) {
        if (fb && typeof fb === 'object' && k in fb) {
          fb = fb[k];
        } else {
          fb = undefined;
          break;
        }
      }
      return fb !== undefined && typeof fb === 'string' ? fb : fallback || path;
    };
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
