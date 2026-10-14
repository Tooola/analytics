/**
 * Open Analytics AI — Frontend API Client
 * Connects directly to FastAPI backend (local or production).
 */

const DEFAULT_API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const TOKEN_KEY = 'oak_token';

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

// ─── Dashboard session (JWT from POST /auth/login) ────────────────────────

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

export function setAuthToken(token) {
  if (!token) {
    localStorage.removeItem(TOKEN_KEY);
  } else {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearAuthToken() {
  localStorage.removeItem(TOKEN_KEY);
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

  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    // Send the dashboard JWT when a session exists (admin routes need it).
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      // Session expired / revoked → force back to the login page.
      if (response.status === 401 && endpoint !== '/api/v1/auth/login' && getAuthToken()) {
        window.dispatchEvent(new CustomEvent('oak:unauthorized'));
      }
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

  // Dashboard authentication
  login: ({ username, password }) =>
    request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  me: () => request('/api/v1/auth/me'),

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

  // Consolidated multi-dataset analysis (one pass, cross links + synthesis)
  analyzeMulti: ({ application, datasets, analysis, payloads, join_key, include_ai = true, apiKey }) =>
    request('/api/v1/analyze/multi', {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey || getStoredApiKey(),
      },
      body: JSON.stringify({
        application,
        datasets,
        analysis,
        payloads,
        ...(join_key ? { join_key } : {}),
        include_ai,
      }),
    }),
};
