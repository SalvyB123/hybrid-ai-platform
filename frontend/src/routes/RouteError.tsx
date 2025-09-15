// frontend/src/routes/RouteError.tsx
import { isRouteErrorResponse, useRouteError } from "react-router-dom";

export default function RouteError() {
  const err = useRouteError();
  if (isRouteErrorResponse(err)) {
    return (
      <main className="p-6">
        <h1 className="text-xl font-semibold">Route error</h1>
        <p className="mt-2 text-sm text-destructive-foreground">
          {err.status} {err.statusText}
        </p>
      </main>
    );
  }
  return (
    <main className="p-6">
      <h1 className="text-xl font-semibold">Unexpected error</h1>
      <pre className="mt-2 text-sm">{String(err)}</pre>
    </main>
  );
}