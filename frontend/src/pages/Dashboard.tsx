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
import { SentimentRecord, fetchSentiments } from "@/lib/api";

type ChartDatum = { name: string; count: number };

export default function Dashboard() {
    const [data, setData] = React.useState<SentimentRecord[] | null>(null);
    const [error, setError] = React.useState<string | null>(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const controller = new AbortController();
        async function load() {
            try {
                setLoading(true);
                setError(null);
                const items = await fetchSentiments();
                setData(items);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load");
            } finally {
                setLoading(false);
            }
        }
        load();
        return () => controller.abort();
    }, []);

    const counts = React.useMemo(() => {
        const pos = data?.filter((d) => d.label === "positive").length ?? 0;
        const neg = data?.filter((d) => d.label === "negative").length ?? 0;
        // If you want to show neutral later:
        // const neu = data?.filter(d => d.label === "neutral").length ?? 0;

        const chart: ChartDatum[] = [
            { name: "Positive", count: pos },
            { name: "Negative", count: neg },
        ];
        return { chart, total: data?.length ?? 0, pos, neg };
    }, [data]);

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

                {!loading && !error && (
                    <>
                        <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
                            <div className="rounded-xl border p-4">
                                <p className="text-sm text-muted-foreground">
                                    Total
                                </p>
                                <p className="text-2xl font-semibold">
                                    {counts.total}
                                </p>
                            </div>
                            <div className="rounded-xl border p-4">
                                <p className="text-sm text-muted-foreground">
                                    Positive
                                </p>
                                <p className="text-2xl font-semibold text-green-600 dark:text-green-400">
                                    {counts.pos}
                                </p>
                            </div>
                            <div className="rounded-xl border p-4">
                                <p className="text-sm text-muted-foreground">
                                    Negative
                                </p>
                                <p className="text-2xl font-semibold text-red-600 dark:text-red-400">
                                    {counts.neg}
                                </p>
                            </div>
                        </section>

                        <section className="rounded-xl border p-4 h-[360px]">
                            <h2 className="text-lg font-medium mb-3">
                                Sentiment (Positive vs Negative)
                            </h2>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={counts.chart}
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
                                    <Bar
                                        dataKey="count"
                                        name="Count" /* Let default colours apply */
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        </section>
                    </>
                )}
            </div>
        </main>
    );
}
