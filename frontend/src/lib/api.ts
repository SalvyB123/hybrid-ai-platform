// frontend/src/lib/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type SentimentSummary = {
    positive: number;
    negative: number;
    neutral: number;
    total: number;
};

type FetchOptions = { signal?: AbortSignal; timeoutMs?: number };

async function apiGet<T>(path: string, opts: FetchOptions = {}): Promise<T> {
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

export function fetchSentimentSummary(): Promise<SentimentSummary> {
    return apiGet<SentimentSummary>("/sentiment/summary");
}
