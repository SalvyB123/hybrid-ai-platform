// frontend/src/pages/Dashboard.tsx
import * as React from "react";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import Spinner from "@/components/ui/spinner";
import type { SentimentSummary } from "@/lib/api";
import { fetchSentimentSummary } from "@/lib/api";

type ChartDatum = { name: string; count: number };

export default function Dashboard() {
    const [summary, setSummary] = React.useState<SentimentSummary | null>(null);
    const [error, setError] = React.useState<string | null>(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        let alive = true;
        (async () => {
            try {
                setLoading(true);
                setError(null);
                const s = await fetchSentimentSummary();
                if (alive) setSummary(s);
            } catch (err) {
                if (alive)
                    setError(
                        err instanceof Error ? err.message : "Failed to load",
                    );
            } finally {
                if (alive) setLoading(false);
            }
        })();
        return () => {
            alive = false;
        };
    }, []);

    const chartData: ChartDatum[] = React.useMemo(
        () => [
            { name: "Positive", count: summary?.positive ?? 0 },
            { name: "Negative", count: summary?.negative ?? 0 },
            // Add Neutral later if you want a third bar
        ],
        [summary],
    );

    return (
        <main className="min-h-screen bg-background text-foreground p-6">
            <div className="container mx-auto max-w-6xl">
                <header className="mb-6">
                    <h1 className="text-2xl font-semibold">
                        Sentiment Dashboard
                    </h1>
                    <p className="text-sm text-muted-foreground">
                        Overview of recent sentiment submissions from the API.
                    </p>
                </header>

                {loading && (
                    <div className="mt-10">
                        <Spinner label="Loading sentiment data…" />
                    </div>
                )}

                {error && (
                    <div className="mt-6 rounded-md border border-destructive/30 bg-destructive/5 p-4">
                        <p className="text-destructive font-medium">
                            Failed to load
                        </p>
                        <p className="text-sm text-muted-foreground">{error}</p>
                    </div>
                )}

                {!loading && !error && summary && (
                    <>
                        <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-4">
                            <div
                                className="rounded-xl border p-4"
                                data-testid="metric-total"
                            >
                                <p className="text-sm text-muted-foreground">
                                    Total
                                </p>
                                <p className="text-2xl font-semibold">
                                    {summary.total}
                                </p>
                            </div>
                            <div
                                className="rounded-xl border p-4"
                                data-testid="metric-positive"
                            >
                                <p className="text-sm text-muted-foreground">
                                    Positive
                                </p>
                                <p className="text-2xl font-semibold text-green-600 dark:text-green-400">
                                    {summary.positive}
                                </p>
                            </div>
                            <div
                                className="rounded-xl border p-4"
                                data-testid="metric-negative"
                            >
                                <p className="text-sm text-muted-foreground">
                                    Negative
                                </p>
                                <p className="text-2xl font-semibold text-red-600 dark:text-red-400">
                                    {summary.negative}
                                </p>
                            </div>
                            <div
                                className="rounded-xl border p-4"
                                data-testid="metric-neutral"
                            >
                                <p className="text-sm text-muted-foreground">
                                    Neutral
                                </p>
                                <p className="text-2xl font-semibold">
                                    {summary.neutral}
                                </p>
                            </div>
                        </section>

                        <section className="rounded-xl border p-4 h-[360px]">
                            <h2 className="text-lg font-medium mb-3">
                                Sentiment (Positive vs Negative)
                            </h2>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={chartData}
                                    margin={{
                                        top: 10,
                                        right: 10,
                                        left: 0,
                                        bottom: 0,
                                    }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis allowDecimals={false} />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="count" name="Count" />
                                </BarChart>
                            </ResponsiveContainer>
                        </section>
                    </>
                )}
            </div>
        </main>
    );
}
