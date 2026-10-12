import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function KpiCard({ title, value, subtext, trend, icon: Icon, color = 'indigo' }) {
  const colorMap = {
    indigo: 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/20',
    emerald: 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20',
    rose: 'text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/20',
    amber: 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20',
    sky: 'text-sky-600 dark:text-sky-400 bg-sky-50 dark:bg-sky-500/10 border-sky-200 dark:border-sky-500/20',
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-xl border ${colorMap[color] || colorMap.indigo}`}>
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <div className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">{value}</div>
        {trend && (
          <div
            className={`flex items-center text-xs font-medium px-2 py-0.5 rounded-full ${
              trend.direction === 'up'
                ? 'text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/40'
                : trend.direction === 'down'
                ? 'text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800/40'
                : 'text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700'
            }`}
          >
            {trend.direction === 'up' && <ArrowUpRight className="h-3 w-3 mr-0.5" />}
            {trend.direction === 'down' && <ArrowDownRight className="h-3 w-3 mr-0.5" />}
            {trend.direction === 'stable' && <Minus className="h-3 w-3 mr-0.5" />}
            <span>{trend.value}</span>
          </div>
        )}
      </div>

      {subtext && <p className="mt-2 text-xs text-slate-500 dark:text-slate-400 truncate">{subtext}</p>}
    </div>
  );
}
