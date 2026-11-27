import React, { useState } from 'react';
import { 
  AreaChart, Area, 
  BarChart, Bar, 
  LineChart, Line, 
  ResponsiveContainer, 
  CartesianGrid, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend 
} from 'recharts';
import { LayoutGrid, Code2, Copy, Check, Sparkles } from 'lucide-react';

export const CHART_TEMPLATES = [
  {
    id: 'area-smooth',
    name: 'Aires Lissées (Vue Tendance Moderne)',
    description: 'Courbe avec remplissage en dégradé, idéale pour lisser les dynamiques temporelles.',
    type: 'area',
  },
  {
    id: 'bars-grouped',
    name: 'Barres Verticales (Comparaison Périodique)',
    description: 'Barres catégorisées pour comparer directement le volume de chaque période.',
    type: 'bar',
  },
  {
    id: 'lines-crisp',
    name: 'Lignes Précises avec Points (Précision Métrique)',
    description: 'Tracé linéaire mettant en valeur chaque point d’observation sans lissage.',
    type: 'line',
  },
  {
    id: 'kpi-cards',
    name: 'Cartes Synthétiques KPI (Lecture Exécutive)',
    description: 'Affichage épuré sous forme de cartes d’indicateurs et deltas, sans graphique dense.',
    type: 'kpi',
  }
];

export default function DynamicChartRenderer({
  title,
  subtitle,
  data,
  metrics = [],
  xAxisKey = 'periode',
  height = 240,
}) {
  const [activeTemplate, setActiveTemplate] = useState('area-smooth');
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);

  const colors = ['#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#3b82f6'];

  const handleCopyCode = () => {
    const codeSnippet = `// Template Recharts : ${activeTemplate}
import { ResponsiveContainer, ${activeTemplate.includes('area') ? 'AreaChart, Area' : activeTemplate.includes('bar') ? 'BarChart, Bar' : 'LineChart, Line'}, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts';

export function MonGraphique({ data }) {
  return (
    <ResponsiveContainer width="100%" height={${height}}>
      <${activeTemplate.includes('area') ? 'AreaChart' : activeTemplate.includes('bar') ? 'BarChart' : 'LineChart'} data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.15} />
        <XAxis dataKey="${xAxisKey}" tick={{ fontSize: 11, fill: '#94a3b8' }} />
        <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
        <Tooltip />
        <Legend />
        ${metrics.map((m, i) => `<${activeTemplate.includes('area') ? 'Area' : activeTemplate.includes('bar') ? 'Bar' : 'Line'} type="monotone" dataKey="${m.key || m}" stroke="${m.color || colors[i % colors.length]}" fill="${m.color || colors[i % colors.length]}" />`).join('\n        ')}
      </${activeTemplate.includes('area') ? 'AreaChart' : activeTemplate.includes('bar') ? 'BarChart' : 'LineChart'}>
    </ResponsiveContainer>
  );
}`;
    navigator.clipboard.writeText(codeSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 shadow-xs flex flex-col justify-between">
      {/* Header avec switch de templates */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800/80 pb-3">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-200">
            {title}
          </h4>
          {subtitle && (
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">{subtitle}</p>
          )}
        </div>

        {/* Sélecteur de Template Interchangeable */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl text-xs">
            <LayoutGrid className="h-3.5 w-3.5 text-slate-400 ml-1.5" />
            <select
              value={activeTemplate}
              onChange={(e) => setActiveTemplate(e.target.value)}
              className="bg-transparent text-slate-800 dark:text-slate-200 text-[11px] font-semibold pr-2 focus:outline-none cursor-pointer"
            >
              {CHART_TEMPLATES.map((tmpl) => (
                <option key={tmpl.id} value={tmpl.id} className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200">
                  {tmpl.name}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={() => setShowCode(!showCode)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-xl border border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            title="Copier le snippet pour les développeurs"
          >
            <Code2 className="h-3.5 w-3.5 text-indigo-500" />
            <span className="hidden sm:inline">Code Développeur</span>
          </button>
        </div>
      </div>

      {/* Code Snippet Modal/Drawer */}
      {showCode && (
        <div className="mb-4 p-3 bg-slate-950 text-slate-200 rounded-xl font-mono text-[11px] relative border border-slate-800">
          <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-800 text-[10px] text-slate-400">
            <span className="flex items-center gap-1.5">
              <Sparkles className="h-3 w-3 text-indigo-400" />
              Template React / Recharts prêt à intégrer
            </span>
            <button
              onClick={handleCopyCode}
              className="flex items-center gap-1 px-2 py-0.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-sans text-[10px]"
            >
              {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
              {copied ? 'Copié !' : 'Copier'}
            </button>
          </div>
          <pre className="overflow-x-auto p-1 leading-relaxed text-indigo-300">
            {`// Template actif : ${activeTemplate}\n// Données attendues : [{ ${xAxisKey}: '...', ${metrics.map(m => (m.key || m) + ': 10').join(', ')} }]`}
          </pre>
        </div>
      )}

      {/* Rendu Graphique Selon Template Sélectionné */}
      <div>
        {activeTemplate === 'area-smooth' && (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={data} margin={{ top: 6, right: 12, bottom: 0, left: -20 }}>
              <defs>
                {metrics.map((m, idx) => {
                  const col = m.color || colors[idx % colors.length];
                  const key = m.key || m;
                  return (
                    <linearGradient key={key} id={`g-${key}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={col} stopOpacity={0.25} />
                      <stop offset="100%" stopColor={col} stopOpacity={0.01} />
                    </linearGradient>
                  );
                })}
              </defs>
              <CartesianGrid stroke="#94a3b8" strokeOpacity={0.15} strokeDasharray="3 3" />
              <XAxis dataKey={xAxisKey} tick={{ fontSize: 11, fill: '#94a3b8' }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
              {metrics.map((m, idx) => {
                const col = m.color || colors[idx % colors.length];
                const key = m.key || m;
                return (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    name={m.label || key}
                    stroke={col}
                    strokeWidth={2}
                    fill={`url(#g-${key})`}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                );
              })}
            </AreaChart>
          </ResponsiveContainer>
        )}

        {activeTemplate === 'bars-grouped' && (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart data={data} margin={{ top: 6, right: 12, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="#94a3b8" strokeOpacity={0.15} strokeDasharray="3 3" />
              <XAxis dataKey={xAxisKey} tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
              {metrics.map((m, idx) => {
                const col = m.color || colors[idx % colors.length];
                const key = m.key || m;
                return (
                  <Bar
                    key={key}
                    dataKey={key}
                    name={m.label || key}
                    fill={col}
                    radius={[4, 4, 0, 0]}
                  />
                );
              })}
            </BarChart>
          </ResponsiveContainer>
        )}

        {activeTemplate === 'lines-crisp' && (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={data} margin={{ top: 6, right: 12, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="#94a3b8" strokeOpacity={0.15} strokeDasharray="3 3" />
              <XAxis dataKey={xAxisKey} tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
              {metrics.map((m, idx) => {
                const col = m.color || colors[idx % colors.length];
                const key = m.key || m;
                return (
                  <Line
                    key={key}
                    type="linear"
                    dataKey={key}
                    name={m.label || key}
                    stroke={col}
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: col }}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        )}

        {activeTemplate === 'kpi-cards' && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 py-2">
            {metrics.map((m, idx) => {
              const col = m.color || colors[idx % colors.length];
              const key = m.key || m;
              const lastVal = data && data.length > 0 ? data[data.length - 1][key] : '—';
              const firstVal = data && data.length > 1 ? data[0][key] : null;
              const diff = typeof lastVal === 'number' && typeof firstVal === 'number' ? lastVal - firstVal : null;

              return (
                <div
                  key={key}
                  className="rounded-xl p-3 flex flex-col justify-between"
                  style={{ background: col + '10', border: `1px solid ${col}25` }}
                >
                  <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 truncate">
                    {m.label || key}
                  </span>
                  <div className="my-2">
                    <span className="text-2xl font-bold" style={{ color: col }}>
                      {typeof lastVal === 'number' ? lastVal.toLocaleString() : lastVal}
                    </span>
                  </div>
                  {diff !== null && (
                    <span className={`text-[10px] font-semibold ${diff >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {diff > 0 ? `▲ +${diff.toLocaleString()}` : diff < 0 ? `▼ ${diff.toLocaleString()}` : '→ Stable'}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
