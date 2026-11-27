"use strict";
/**
 * Open Analytics AI — Official TypeScript Client
 * Lightweight, zero-dependency SDK for decision intelligence and causal analysis.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AnalyticsClient = exports.AnalyticsError = void 0;
class AnalyticsError extends Error {
    statusCode;
    responseBody;
    constructor(message, statusCode, responseBody) {
        super(message);
        this.name = 'AnalyticsError';
        this.statusCode = statusCode;
        this.responseBody = responseBody;
    }
}
exports.AnalyticsError = AnalyticsError;
class AnalyticsClient {
    apiKey;
    baseUrl;
    timeout;
    constructor(options = {}) {
        this.apiKey = options.apiKey;
        this.baseUrl = (options.baseUrl || 'https://api.ainalytics.j-ola-sun.com').replace(/\/+$/, '');
        this.timeout = options.timeout || 30000;
    }
    async request(path, method = 'GET', body, useApiKey = true) {
        const url = `${this.baseUrl}${path}`;
        const headers = {
            'Content-Type': 'application/json',
            Accept: 'application/json',
            'User-Agent': 'OpenAnalyticsAI-TypeScriptSDK/0.1.0',
        };
        if (useApiKey && this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeout);
        try {
            const response = await fetch(url, {
                method,
                headers,
                body: body ? JSON.stringify(body) : undefined,
                signal: controller.signal,
            });
            clearTimeout(timer);
            if (!response.ok) {
                let errBody = null;
                try {
                    errBody = await response.json();
                }
                catch {
                    // Non-JSON response
                }
                const detail = (errBody && typeof errBody === 'object' && 'detail' in errBody)
                    ? String(errBody.detail)
                    : response.statusText;
                throw new AnalyticsError(`HTTP ${response.status}: ${detail}`, response.status, errBody);
            }
            return (await response.json());
        }
        catch (err) {
            clearTimeout(timer);
            if (err instanceof AnalyticsError)
                throw err;
            const msg = err instanceof Error ? err.message : String(err);
            throw new AnalyticsError(`Connection error to ${this.baseUrl}: ${msg}`);
        }
    }
    /**
     * Health check
     */
    async health() {
        return this.request('/api/v1/health', 'GET', undefined, false);
    }
    /**
     * One-line instant analysis of raw JSON records without pre-registration.
     */
    async quickAnalyze(params) {
        return this.request('/api/v1/analyze/quick', 'POST', {
            data: params.data,
            analysis: params.analysis || ['auto'],
            include_ai: params.includeAi ?? true,
            label: params.label || 'quick-test',
            ...(params.groupBy ? { group_by: params.groupBy } : {}),
            ...(params.language ? { language: params.language } : {}),
        }, false);
    }
    /**
     * Submit data to a registered application & dataset using API key.
     */
    async analyze(params) {
        if (!this.apiKey) {
            throw new AnalyticsError('apiKey is required for analyze(). Pass apiKey to AnalyticsClient constructor.');
        }
        return this.request('/api/v1/analyze', 'POST', {
            application: params.application,
            dataset: params.dataset,
            data: params.data,
            analysis: params.analysis || ['auto'],
            include_ai: params.includeAi ?? true,
            ...(params.groupBy ? { group_by: params.groupBy } : {}),
            ...(params.language ? { language: params.language } : {}),
        }, true);
    }
    /**
     * Consolidated multi-dataset analysis in a single pass.
     */
    async analyzeMulti(params) {
        if (!this.apiKey) {
            throw new AnalyticsError('apiKey is required for analyzeMulti().');
        }
        return this.request('/api/v1/analyze/multi', 'POST', {
            application: params.application,
            datasets: params.datasets,
            payloads: params.payloads,
            analysis: params.analysis || ['auto'],
            include_ai: params.includeAi ?? true,
            ...(params.joinKey ? { join_key: params.joinKey } : {}),
            ...(params.groupBy ? { group_by: params.groupBy } : {}),
            ...(params.language ? { language: params.language } : {}),
        }, true);
    }
    /**
     * Compare two periods (Period A vs Period B).
     * Automatically identifies improvements, degradations, and new points of attention.
     */
    async compare(params) {
        const normA = Array.isArray(params.periodA)
            ? { label: params.periodALabel || 'Période A', data: params.periodA }
            : params.periodA;
        const normB = Array.isArray(params.periodB)
            ? { label: params.periodBLabel || 'Période B', data: params.periodB }
            : params.periodB;
        return this.request('/api/v1/analyze/quick/compare', 'POST', {
            period_a: normA,
            period_b: normB,
            label: params.label || 'comparatif-temporel',
            include_ai: params.includeAi ?? true,
            ...(params.language ? { language: params.language } : {}),
        }, false);
    }
}
exports.AnalyticsClient = AnalyticsClient;
