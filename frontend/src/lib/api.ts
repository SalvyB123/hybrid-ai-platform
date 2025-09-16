// frontend/src/lib/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type SentimentRecord = {
    id: string;
    text: string;
    score: number;
    label: "positive" | "negative" | "neutral";
    created_at?: string;
};

export type SentimentSummary = {
    positive: number;
    negative: number;
    neutral: number;
    total: number;
};

type FetchOptions = {
    signal?: AbortSignal;
    timeoutMs?: number;
};

export async function apiGet<T>(
    path: string,
    opts: FetchOptions = {},
): Promise<T> {
    const controller = new AbortController();
    const timeout = setTimeout(
        () => controller.abort(),
        opts.timeoutMs ?? 8000,
    );

    try {
        const res = await fetch(`${BASE_URL}${path}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            signal: opts.signal ?? controller.signal,
        });
        if (!res.ok) {
            const text = await res.text().catch(() => "");
            throw new Error(
                `GET ${path} failed: ${res.status} ${res.statusText} ${text}`,
            );
        }
        return (await res.json()) as T;
    } finally {
        clearTimeout(timeout);
    }
}

/** Fetch aggregated counts for the dashboard */
export async function fetchSentimentSummary(): Promise<SentimentSummary> {
    return apiGet<SentimentSummary>("/sentiment/summary");
}

/** (Optional) Keep this if/when you add GET /sentiment */
export async function fetchSentiments(limit = 100): Promise<SentimentRecord[]> {
    // This will 405 until a list endpoint exists on the backend.
    return apiGet<SentimentRecord[]>(
        `/sentiment?limit=${encodeURIComponent(limit)}`,
    );
}
