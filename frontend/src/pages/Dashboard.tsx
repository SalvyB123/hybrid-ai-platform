import { Button } from "@/components/ui/button";
import { clearToken, getToken } from "@/lib/auth";

export default function DashboardPage() {
  const token = getToken();

  return (
    <main className="min-h-screen bg-background text-foreground flex items-center">
      <div className="container">
        <div className="mx-auto max-w-xl rounded-2xl border p-8 shadow-sm space-y-4">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            This is a stub. You are “signed in” with a dummy JWT stored in localStorage.
          </p>
          <pre className="whitespace-pre-wrap break-all text-xs bg-muted p-3 rounded-md">
{token ?? "No token present"}
          </pre>
          <div>
            <Button
              variant="secondary"
              onClick={() => {
                clearToken();
                location.href = "/login";
              }}
            >
              Sign out
            </Button>
          </div>
        </div>
      </div>
    </main>
  );
}
