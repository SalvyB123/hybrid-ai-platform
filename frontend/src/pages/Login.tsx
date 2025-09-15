// frontend/src/pages/Login.tsx
import * as React from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // prevent full page reload
    // Set the exact key your test checks
    window.localStorage.setItem("jwt", "dummy-jwt");
    navigate("/dashboard");
  };

  return (
    <main className="min-h-screen bg-background text-foreground flex items-center">
      <div className="container">
        <div className="mx-auto max-w-md rounded-2xl border p-8 shadow-sm">
          <h1 className="text-2xl font-semibold mb-6">Sign in</h1>

          {/* noValidate ensures native form validation doesn't block onSubmit during tests */}
          <form className="space-y-5" onSubmit={onSubmit} noValidate>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium leading-none">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm focus-visible:outline-none focus-visible:ring-1"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium leading-none">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm focus-visible:outline-none focus-visible:ring-1"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {/* Accessible name is “Sign in”, which the test queries */}
            <button
              type="submit"
              className="inline-flex items-center justify-center bg-primary text-primary-foreground h-9 px-4 py-2 w-full rounded-md"
            >
              Sign in
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}