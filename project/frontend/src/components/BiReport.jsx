import React, { useState } from 'react';
import { 
  Sparkles, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  ShieldAlert, 
  BarChart3, 
  Table as TableIcon,
  ChevronRight,
  Clock,
  Layers,
  ArrowRight,
  PieChart,
  Lightbulb
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar
} from 'recharts';
import { useTheme } from '../context/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';

// Transforme un nom de colonne technique en libellé lisible
function humanizeCol(name) {
  if (!name) return name;
  const unitMap = {
    '_kg': ' (kg)', '_mm': ' (mm)', '_c': ' (°C)', '_pct': ' (%)',
    '_percent': ' (%)', '_eur': ' (€)', '_euro': ' (€)', '_usd': ' ($)',
    '_h': ' (h)', '_ha': ' (ha)', '_m': ' (m)', '_km': ' (km)',
  };
  let label = name;
  let unit = '';
  for (const [suffix, display] of Object.entries(unitMap)) {
    if (name.toLowerCase().endsWith(suffix)) {
      label = name.slice(0, -suffix.length);
      unit = display;
      break;
    }
  }
  return label.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).trim() + unit;
}

// Finds a row identifier to display instead of "Row #N"
function rowAlias(row, idx) {
  if (!row) return `Observation ${idx + 1}`;
  const idKeys = ['date', 'mois', 'month', 'semaine', 'week', 'periode', 'period',
                  'id', 'nom', 'name', 'region', 'label', 'reference', 'ref', 'code'];
  for (const k of idKeys) {
    if (row[k] !== undefined && row[k] !== null && String(row[k]).length < 50) {
      return String(row[k]);
    }
  }
  return `Observation ${idx + 1}`;
}

export default function BiReport({ report, rawData }) {
  const [activeView, setActiveView] = useState('insights'); // 'insights' | 'charts' | 'data'
  const { theme } = useTheme();
  const { language, t } = useLanguage();

  if (!report) return null;

  const results = report.results || {};
  const summary = results.summary || [];
  const trends = results.trend || [];
  const anomalies = results.anomaly || [];
  const causality = results.causality || [];
  const grouped = results.grouped || null;
  const insights = report.insights || [];

  // Parse AI Interpretation
  let ai = null;
  if (report.ai_interpretation) {
    try {
      ai = typeof report.ai_interpretation === 'string'
        ? JSON.parse(report.ai_interpretation)
        : report.ai_interpretation;
    } catch {
      ai = null;
    }
  }

  // Identify numeric keys for charts
  const sampleRow = (rawData && rawData[0]) ? rawData[0] : {};
  const numericColumns = Object.keys(sampleRow).filter(k => {
    const val = sampleRow[k];
    return typeof val === 'number' || (!isNaN(Number(val)) && val !== '' && val !== null);
  });

  // Prepare chart series from raw data
  const chartData = (rawData || []).slice(0, 100).map((row, idx) => ({
    _index: idx + 1,
    ...row,
  }));

  const totalAnomalies = anomalies.reduce((acc, curr) => acc + (curr.count || 0), 0);

  const isDark = theme === 'dark';
  const gridStroke = isDark ? '#1e293b' : '#e2e8f0';
  const axisStroke = isDark ? '#64748b' : '#94a3b8';
  const tooltipBg = isDark ? '#0f172a' : '#ffffff';
  const tooltipBorder = isDark ? '#334155' : '#cbd5e1';
  const tooltipText = isDark ? '#f8fafc' : '#0f172a';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Report Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
            <Layers className="h-3.5 w-3.5" />
            <span>{t('report.header_badge', 'Analytical & Decision Synthesis')}</span>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span className="text-slate-500 dark:text-slate-400">
              {report.row_count || rawData?.length || 0} {t('report.records', 'records')}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
            {report.label || report.dataset || t('report.default_title', 'Performance Report')}
          </h2>
        </div>

        {/* View Switcher */}
        <div className="flex bg-slate-100 dark:bg-slate-950 p-1 rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
          <button
            onClick={() => setActiveView('insights')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              activeView === 'insights' 
                ? 'bg-indigo-600 text-white shadow-sm' 
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{t('report.view_results', 'Results & Recommendations')}</span>
          </button>
          <button
            onClick={() => setActiveView('charts')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              activeView === 'charts' 
                ? 'bg-indigo-600 text-white shadow-sm' 
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <BarChart3 className="h-3.5 w-3.5" />
            <span>{t('report.view_charts', 'Charts')} ({numericColumns.length})</span>
          </button>
          <button
            onClick={() => setActiveView('data')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              activeView === 'data' 
                ? 'bg-indigo-600 text-white shadow-sm' 
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <TableIcon className="h-3.5 w-3.5" />
            <span>{t('report.view_raw', 'Raw Data')} ({rawData?.length || 0})</span>
          </button>
        </div>
      </div>

      {/* Top Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm transition-colors">
          <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
            {t('report.card_data_analyzed', 'Analyzed Data')}
          </span>
          <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{numericColumns.length}</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{t('report.card_indicators', 'measured indicators')}</p>
        </div>
        <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm transition-colors">
          <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
            {t('report.card_trends', 'Trends Detected')}
          </span>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{trends.length}</div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{t('report.card_directional', 'Directional trend')}</p>
        </div>
        <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm transition-colors">
          <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
            {t('report.card_watchpoints', 'Points de vigilance')}
          </span>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className={`text-2xl font-bold ${totalAnomalies > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-white'}`}>
              {totalAnomalies}
            </span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              totalAnomalies > 0 
                ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300' 
                : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
            }`}>
              {totalAnomalies > 0 ? t('report.card_status_warn', 'À vérifier') : t('report.card_status_ok', 'Normal')}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {totalAnomalies > 0 ? t('report.card_sub_warn', 'Valeurs anormales') : t('report.card_sub_ok', 'Tout est normal')}
          </p>
        </div>
        <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm transition-colors">
          <span className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
            {t('report.card_analyzed_by', 'Analyzed by')}
          </span>
          <div className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 mt-2 truncate flex items-center gap-2">
            {ai?.provider || t('report.card_engine', 'Statistical Engine')}
            {report.ai_status && (
              <span
                className={`inline-block w-2 h-2 rounded-full shrink-0 ${
                  report.ai_status === 'ok'
                    ? 'bg-emerald-500'
                    : 'bg-rose-500'
                }`}
              />
            )}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{t('report.card_strategic', 'Strategic recommendations')}</p>
        </div>
      </div>

      {/* VIEW: RESULTS & RECOMMENDATIONS */}
      {activeView === 'insights' && (
        <div className="space-y-6">
          {/* Executive AI Block */}
          {ai && (
            <div className="bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-500/30 rounded-2xl p-6 shadow-sm transition-colors">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4 mb-5">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">{t('report.ai_title', 'Executive Assessment & Strategic Guidance')}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{t('report.ai_subtitle', 'Tailored reporting for executive leadership')}</p>
                  </div>
                </div>
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/40">
                  {t('report.reliability', 'Reliability')} : {Math.round((ai.confidence || 0.95) * 100)}%
                </span>
              </div>

              {/* Executive Summary */}
              {ai.summary && (
                <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed mb-6">
                  <div className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1.5">
                    {t('report.executive_summary', 'Executive Summary')}
                  </div>
                  {ai.summary}
                </div>
              )}

              {/* Key Findings & Recommendations Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Key Findings */}
                {ai.key_findings && ai.key_findings.length > 0 && (
                  <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                      <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                      {t('report.key_findings', 'Key Findings')}
                    </h4>
                    <ul className="space-y-2.5">
                      {ai.key_findings.map((finding, idx) => (
                        <li key={idx} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                          <span className="text-indigo-600 dark:text-indigo-400 font-bold mt-0.5">•</span>
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {ai.recommendations && ai.recommendations.length > 0 && (
                  <div className="bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                      <CheckCircle className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mr-2" />
                      {t('report.recommendations', 'Decision Recommendations')}
                    </h4>
                    <ul className="space-y-2.5">
                      {ai.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-xs text-slate-600 dark:text-slate-300 flex items-start space-x-2">
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold mt-0.5">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Action Plan */}
              {ai.action_plan && ai.action_plan.length > 0 && (
                <div className="mt-6 border-t border-slate-100 dark:border-slate-800 pt-5">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-3 flex items-center">
                    <Clock className="h-4 w-4 text-sky-600 dark:text-sky-400 mr-2" />
                    {t('report.action_plan', 'Recommended Action Plan')}
                  </h4>
                  <div className="space-y-2.5">
                    {ai.action_plan.map((step, idx) => {
                      const cleanStep = step.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();
                      return (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start space-x-3">
                          <ArrowRight className="h-4 w-4 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                          <span className="leading-relaxed">{cleanStep}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Risk Assessment */}
              {ai.risk_assessment && (
                <div className="mt-5 p-3.5 rounded-xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/30 flex items-start space-x-3 text-xs text-amber-800 dark:text-amber-200">
                  <ShieldAlert className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold uppercase tracking-wider text-[11px] block">
                      {t('report.critical_watchpoints', 'Priority Watchpoints')} :
                    </span>
                    <span className="leading-relaxed">{ai.risk_assessment}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Causality drivers */}
          {causality.length > 0 && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center">
                <Lightbulb className="h-4 w-4 text-amber-500 mr-2 shrink-0" />
                {t('report.causality_title', 'Explanatory Factors & Variation Drivers')}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {causality.map((driver, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start space-x-2.5">
                    <span className="text-amber-500 font-bold mt-0.5">•</span>
                    <span className="leading-relaxed">{driver.explanation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Segments (group_by) */}
          {grouped && (grouped.segments || []).length > 0 && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm transition-colors">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-1 flex items-center">
                <PieChart className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mr-2" />
                {t('report.segments_by', 'Breakdown by')} {humanizeCol(grouped.group_by)}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-5">
                {t('report.ranked_by', 'Ranked by')} {humanizeCol(grouped.ranked_by)} · {grouped.segment_count} {t('report.segment', 'segment')}{(grouped.segment_count || 0) === 1 ? '' : 's'}
                {grouped.note ? ` · ${grouped.note}` : ''}
              </p>
              <div className="space-y-3">
                {grouped.segments.map((seg) => {
                  const m = (grouped.ranked_by && seg.metrics[grouped.ranked_by]) || null;
                  const pct = m && m.share != null ? Math.round(m.share * 1000) / 10 : null;
                  return (
                    <div key={seg.segment} className="flex items-center gap-3">
                      <span className="text-xs font-mono text-slate-400 dark:text-slate-500 w-6">#{seg.rank}</span>
                      <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 w-40 truncate" title={seg.segment}>
                        {seg.segment}
                      </span>
                      <div className="flex-1 h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden min-w-[60px]">
                        <div
                          className="h-full bg-indigo-500 dark:bg-indigo-400 rounded-full transition-all"
                          style={{ width: `${pct ?? 0}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-600 dark:text-slate-300 w-16 text-right">
                        {pct != null ? `${pct}%` : '—'}
                      </span>
                      <span className="text-[11px] text-slate-500 dark:text-slate-400 w-52 text-right hidden md:block">
                        {humanizeCol(grouped.ranked_by)} : {t('report.avg', 'avg.')} {m ? m.mean : '—'} · {t('report.total', 'total')} {m ? m.sum : '—'} · {seg.row_count} {t('report.entries', 'entries')}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          {grouped && (grouped.segments || []).length === 0 && grouped.note && (
            <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/30 text-xs text-amber-800 dark:text-amber-200 flex items-start space-x-3">
              <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <span>
                {t('report.segmentation_na', 'Segmentation')} «&nbsp;{humanizeCol(grouped.group_by)}&nbsp;» {t('report.not_applicable', 'not applicable')}: {grouped.note}
              </span>
            </div>
          )}
        </div>
      )}

      {/* VIEW: CHARTS */}
      {activeView === 'charts' && (
        <div className="space-y-6">
          {numericColumns.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
              {t('report.no_numeric_cols', 'No numeric columns detected in the data to draw charts.')}
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {numericColumns.map((col, idx) => {
                const colors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#3b82f6'];
                const colColor = colors[idx % colors.length];
                const colAnom = anomalies.find(a => a.column === col && (a.count || 0) > 0);

                return (
                  <div key={col} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm transition-colors flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white capitalize">{humanizeCol(col)}</h4>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400">{t('report.chart_subtitle', 'Chronological value evolution')}</p>
                        </div>
                      </div>

                      <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={chartData} margin={{ top: 10, right: 15, left: -10, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                            <XAxis dataKey="_index" stroke={axisStroke} tick={{ fontSize: 10 }} />
                            <YAxis stroke={axisStroke} tick={{ fontSize: 10 }} />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: tooltipBg, 
                                borderColor: tooltipBorder, 
                                borderRadius: '8px', 
                                fontSize: '11px',
                                color: tooltipText 
                              }}
                              formatter={(val, name) => [val, humanizeCol(name)]}
                            />
                            <Line
                              type="monotone"
                              dataKey={col}
                              stroke={colColor}
                              strokeWidth={2.5}
                              dot={{ r: 2.5 }}
                              activeDot={{ r: 5 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {colAnom && (
                      <div className="mt-4 p-3 rounded-xl bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 text-xs flex items-start space-x-2.5 text-amber-900 dark:text-amber-200">
                        <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                        <div className="leading-relaxed">
                          <span className="font-semibold block text-[11px] uppercase tracking-wider text-amber-900 dark:text-amber-300">
                            {t('report.anomaly_on_var', 'Attention point on this variable:')}
                          </span>
                          <span>{colAnom.reason || t('report.anomaly_default', 'Exceptional peak or unusual drop detected compared to observed baseline.')}</span>
                          {colAnom.recommendation && (
                            <span className="block mt-1 text-[11px] text-slate-600 dark:text-slate-400">
                              {t('report.action_advised', 'Recommended action:')} {colAnom.recommendation}
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* VIEW: RAW DATA */}
      {activeView === 'data' && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">{t('report.raw_title', 'Record Sample')}</h3>
            <span className="text-xs text-slate-500 font-mono">
              {t('report.showing_rows', 'Showing')} {Math.min(50, rawData?.length || 0)} {t('report.first_rows', 'first rows')}
            </span>
          </div>
          {rawData && rawData.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3 font-mono text-slate-400">#</th>
                    {Object.keys(rawData[0]).map((col) => (
                      <th key={col} className="py-2.5 px-3 font-semibold">{humanizeCol(col)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 bg-white dark:bg-slate-900/40">
                  {rawData.slice(0, 50).map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 text-slate-700 dark:text-slate-300">
                      <td className="py-2 px-3 font-mono text-slate-400">{idx + 1}</td>
                      {Object.keys(rawData[0]).map((col) => (
                        <td key={col} className="py-2 px-3 font-mono">{String(row[col] ?? '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-xs text-slate-500">{t('report.no_raw_data', 'No raw data available.')}</p>
          )}
        </div>
      )}
    </div>
  );
}
