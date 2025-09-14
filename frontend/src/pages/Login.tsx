import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();

    // Minimal “fake” validation
    if (!email || !pwd) return;

    // Stub: set a dummy JWT in localStorage (no real auth yet)
    setToken("dummy.jwt.token");

    // Redirect to dashboard
    navigate("/dashboard");
  }

  return (
    <main className="min-h-screen bg-background text-foreground flex items-center">
      <div className="container">
        <div className="mx-auto max-w-md rounded-2xl border p-8 shadow-sm">
          <h1 className="text-2xl font-semibold mb-6">Sign in</h1>
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={pwd}
                onChange={(e) => setPwd(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
            <Button type="submit" className="w-full">Sign in</Button>
          </form>
        </div>
      </div>
    </main>
  );
}
