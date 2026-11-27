import React from 'react';
import { X, Search, Layers, Info } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

export default function EvidenceModal({ isOpen, onClose, insight }) {
  const { language } = useLanguage();
  const isEn = language === 'en';

  if (!isOpen || !insight) return null;

  let evidence = null;
  if (insight.evidence) {
    try {
      evidence = typeof insight.evidence === 'string' ? JSON.parse(insight.evidence) : insight.evidence;
    } catch {
      evidence = null;
    }
  }

  // Nettoie la syntaxe Markdown (**texte** -> texte) pour un affichage propre
  const cleanMarkdown = (text) => {
    if (!text || typeof text !== 'string') return text;
    return text.replace(/\*\*(.*?)\*\*/g, '$1');
  };

  const analysisTypeLabels = isEn
    ? {
        summary: 'Descriptive Statistics & Distribution',
        trend: 'Linear Trend & Time-Series Evolution',
        anomaly: 'Statistical Anomaly Detection (Z-Score / IQR)',
        forecast: 'Predictive Forecast (Holt-Winters / ARIMA)',
        correlation: 'Cross-Correlation Matrix',
        distribution: 'Normality & Frequency Distribution',
        causality: 'Inference & Causality (Granger / Lagged)',
      }
    : {
        summary: 'Statistiques Descriptives & Distribution',
        trend: 'Tendance Linéaire & Évolution Temporelle',
        anomaly: "Détection d'Anomalies Statistiques (Z-Score / IQR)",
        forecast: 'Projection Prévisionnelle (Modèle Holt-Winters / ARIMA)',
        correlation: 'Matrice de Corrélation Croisée',
        distribution: 'Test de Normalité & Fréquences',
        causality: "Analyse d'Inférence & Causalité (Granger / Délais)",
      };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden transition-all">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/30">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800/80 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Search className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                {isEn ? 'Source Data & Analytics Methodology' : "Données Sources & Méthode d'Analyse"}
              </h3>
              <p className="text-[11px] text-slate-400">
                {isEn ? 'Full decision finding transparency' : 'Transparence du constat décisionnel'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 text-xs">
          {/* Titre du constat */}
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
            <span className="block text-[10px] uppercase font-mono font-bold text-indigo-600 dark:text-indigo-400 tracking-wider mb-1">
              {isEn ? 'Analyzed Finding' : 'Constat analysé'}
            </span>
            <p className="font-semibold text-slate-900 dark:text-white text-xs leading-relaxed">
              {cleanMarkdown(insight.title)}
            </p>
            <p className="text-slate-600 dark:text-slate-300 mt-1 text-[11px] leading-relaxed">
              {cleanMarkdown(insight.description)}
            </p>
          </div>

          {/* Grille des faits / Données sous-jacentes */}
          {evidence ? (
            <div className="space-y-3">
              <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 font-bold">
                <Layers className="h-3.5 w-3.5 text-indigo-500" />
                <span>{isEn ? 'Parameters and Extracted Metrics:' : 'Paramètres et Mesures Extraites :'}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <span className="block text-[10px] text-slate-400 font-sans">
                    {isEn ? 'Calculation method' : 'Méthode de calcul'}
                  </span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">
                    {analysisTypeLabels[evidence.analysis_type] || evidence.analysis_type}
                  </span>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <span className="block text-[10px] text-slate-400 font-sans">
                    {isEn ? 'Analyzed metric' : 'Indicateur analysé'}
                  </span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">
                    {evidence.metric_label || evidence.column || insight.metric || '—'}
                  </span>
                </div>

                {evidence.mean !== undefined && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span className="block text-[10px] text-slate-400 font-sans">
                      {isEn ? 'Observed mean' : 'Moyenne observée'}
                    </span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {typeof evidence.mean === 'number'
                        ? evidence.mean.toLocaleString(isEn ? 'en-US' : 'fr-FR', { maximumFractionDigits: 2 })
                        : evidence.mean}
                    </span>
                  </div>
                )}

                {evidence.median !== undefined && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span className="block text-[10px] text-slate-400 font-sans">
                      {isEn ? 'Observed median' : 'Médiane observée'}
                    </span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {typeof evidence.median === 'number'
                        ? evidence.median.toLocaleString(isEn ? 'en-US' : 'fr-FR', { maximumFractionDigits: 2 })
                        : evidence.median}
                    </span>
                  </div>
                )}

                {evidence.change_pct !== undefined && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span className="block text-[10px] text-slate-400 font-sans">
                      {isEn ? 'Calculated change' : 'Variation calculée'}
                    </span>
                    <span className={`font-semibold ${evidence.change_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {evidence.change_pct > 0 ? `+${evidence.change_pct.toFixed(1)}%` : `${evidence.change_pct.toFixed(1)}%`}
                    </span>
                  </div>
                )}

                {evidence.periods !== undefined && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span className="block text-[10px] text-slate-400 font-sans">
                      {isEn ? 'Observed periods' : 'Périodes observées'}
                    </span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {evidence.periods} {isEn ? 'periods' : 'périodes'}
                    </span>
                  </div>
                )}

                {evidence.count !== undefined && (
                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span className="block text-[10px] text-slate-400 font-sans">
                      {isEn ? 'Row count' : 'Nombre de points'}
                    </span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {evidence.count.toLocaleString(isEn ? 'en-US' : 'fr-FR')}
                    </span>
                  </div>
                )}

                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <span className="block text-[10px] text-slate-400 font-sans">
                    {isEn ? 'Confidence score' : 'Indice de confiance'}
                  </span>
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400">
                    {Math.round((insight.confidence || 1.0) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-slate-500 flex items-center gap-2">
              <Info className="h-4 w-4 shrink-0 text-slate-400" />
              <span>
                {isEn
                  ? `This finding is based on statistical regression and cross-analysis of dataset "${insight.metric || 'analyzed'}".`
                  : `Ce constat s'appuie sur la régression statistique et le recoupement des données du dataset "${insight.metric || 'analysé'}".`}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
