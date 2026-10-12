/**
 * Open Analytics AI — Frontend API Client
 * Connects directly to FastAPI backend (local or production).
 */

const DEFAULT_API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function getApiBase() {
  return localStorage.getItem('oak_api_base') || DEFAULT_API_BASE;
}

export function setApiBase(url) {
  if (!url) {
    localStorage.removeItem('oak_api_base');
  } else {
    localStorage.setItem('oak_api_base', url.replace(/\/+$/, ''));
  }
}

export function getStoredApiKey() {
  return localStorage.getItem('oak_api_key') || '';
}

export function setStoredApiKey(key) {
  if (!key) {
    localStorage.removeItem('oak_api_key');
  } else {
    localStorage.setItem('oak_api_key', key.trim());
  }
}

async function request(endpoint, options = {}) {
  const base = getApiBase();
  const url = `${base}${endpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.detail || data?.error || `HTTP ${response.status} ${response.statusText}`;
      const err = new Error(errorMsg);
      err.status = response.status;
      err.data = data;
      throw err;
    }

    return data;
  } catch (error) {
    if (error.status) throw error;
    // Network / connection error
    const netErr = new Error(`Impossible de contacter l'API à ${base}. Le backend est-il démarré ?`);
    netErr.isNetworkError = true;
    throw netErr;
  }
}

export const api = {
  // System Health
  getHealth: () => request('/api/v1/health'),

  // Quick Analyze (No registration needed)
  quickAnalyze: ({ data, analysis = ['summary', 'trend', 'anomaly'], include_ai = true, label = 'quick-test' }) =>
    request('/api/v1/analyze/quick', {
      method: 'POST',
      body: JSON.stringify({
        data,
        analysis,
        include_ai,
        label,
      }),
    }),

  // Applications
  getApplications: () => request('/api/v1/applications/admin/all'),
  createApplication: ({ name, description }) =>
    request('/api/v1/applications', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    }),
  deleteApplication: (appId) =>
    request(`/api/v1/applications/admin/${appId}`, {
      method: 'DELETE',
    }),
  regenerateApiKey: (appId) =>
    request(`/api/v1/applications/admin/${appId}/regenerate-key`, {
      method: 'POST',
    }),

  // Datasets
  getDatasets: () => request('/api/v1/datasets/all'),
  createDataset: (payload) =>
    request('/api/v1/datasets', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Formal Analysis
  analyze: ({ application, dataset, analysis, data, include_ai = true, apiKey }) =>
    request('/api/v1/analyze', {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey || getStoredApiKey(),
      },
      body: JSON.stringify({
        application,
        dataset,
        analysis,
        data,
        include_ai,
      }),
    }),
};
