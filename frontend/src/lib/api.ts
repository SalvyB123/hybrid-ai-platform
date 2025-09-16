// frontend/src/lib/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type SentimentRecord = {
    id: string;
    text: string;
    score: number;
    label: "positive" | "negative" | "neutral";
    created_at?: string;
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

/**
 * Fetch recent sentiments. The backend may return an array or a paginated shape.
 * This implementation assumes an array endpoint like GET /sentiment.
 * If your API differs (e.g. GET /sentiment?limit=100), adjust here.
 */
export async function fetchSentiments(): Promise<SentimentRecord[]> {
    return apiGet<SentimentRecord[]>("/sentiment");
}
