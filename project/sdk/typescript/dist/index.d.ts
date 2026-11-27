/**
 * Open Analytics AI — Official TypeScript Client
 * Lightweight, zero-dependency SDK for decision intelligence and causal analysis.
 */
export interface ClientOptions {
    apiKey?: string;
    baseUrl?: string;
    timeout?: number;
}
export interface QuickAnalyzeParams {
    data: Record<string, unknown>[];
    analysis?: string[];
    includeAi?: boolean;
    label?: string;
    groupBy?: string;
    language?: 'fr' | 'en';
}
export interface AnalyzeParams {
    application: string;
    dataset: string;
    data: Record<string, unknown>[];
    analysis?: string[];
    includeAi?: boolean;
    groupBy?: string;
    language?: 'fr' | 'en';
}
export interface AnalyzeMultiParams {
    application: string;
    datasets: string[];
    payloads: Record<string, Record<string, unknown>[]>;
    joinKey?: string;
    analysis?: string[];
    includeAi?: boolean;
    groupBy?: string;
    language?: 'fr' | 'en';
}
export interface PeriodInput {
    label: string;
    data: Record<string, unknown>[];
}
export interface CompareParams {
    periodA: PeriodInput | Record<string, unknown>[];
    periodB: PeriodInput | Record<string, unknown>[];
    periodALabel?: string;
    periodBLabel?: string;
    label?: string;
    includeAi?: boolean;
    language?: 'fr' | 'en';
}
export declare class AnalyticsError extends Error {
    statusCode?: number;
    responseBody?: unknown;
    constructor(message: string, statusCode?: number, responseBody?: unknown);
}
export declare class AnalyticsClient {
    private apiKey?;
    private baseUrl;
    private timeout;
    constructor(options?: ClientOptions);
    private request;
    /**
     * Health check
     */
    health(): Promise<{
        status: string;
    }>;
    /**
     * One-line instant analysis of raw JSON records without pre-registration.
     */
    quickAnalyze<T = Record<string, unknown>>(params: QuickAnalyzeParams): Promise<T>;
    /**
     * Submit data to a registered application & dataset using API key.
     */
    analyze<T = Record<string, unknown>>(params: AnalyzeParams): Promise<T>;
    /**
     * Consolidated multi-dataset analysis in a single pass.
     */
    analyzeMulti<T = Record<string, unknown>>(params: AnalyzeMultiParams): Promise<T>;
    /**
     * Compare two periods (Period A vs Period B).
     * Automatically identifies improvements, degradations, and new points of attention.
     */
    compare<T = Record<string, unknown>>(params: CompareParams): Promise<T>;
}
//# sourceMappingURL=index.d.ts.map