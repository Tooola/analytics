import React from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

export default function Modal({ isOpen, onClose, onConfirm, title, message, type = 'info', confirmText = 'Confirmer', cancelText = 'Annuler' }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div 
        className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl p-6 transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center space-x-2.5">
            {type === 'danger' && <AlertCircle className="h-5 w-5 text-rose-500" />}
            {type === 'success' && <CheckCircle className="h-5 w-5 text-emerald-500" />}
            {type === 'info' && <Info className="h-5 w-5 text-indigo-500" />}
            <h3 className="text-base font-bold text-slate-900 dark:text-white">{title}</h3>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="py-4 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          {message}
        </div>

        <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          {onConfirm && (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {cancelText}
            </button>
          )}
          <button
            type="button"
            onClick={() => {
              if (onConfirm) onConfirm();
              else onClose();
            }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold text-white transition-colors shadow-sm ${
              type === 'danger'
                ? 'bg-rose-600 hover:bg-rose-500'
                : 'bg-indigo-600 hover:bg-indigo-500'
            }`}
          >
            {onConfirm ? confirmText : 'OK'}
          </button>
        </div>
      </div>
    </div>
  );
}
