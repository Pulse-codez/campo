"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { api, ApiError, saveTokens, type TokenPair } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const tokens = await api<TokenPair>("/auth/login", {
        method: "POST",
        json: { email, password },
      });
      saveTokens(tokens);
      router.replace("/dashboard");
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? "Email or password is incorrect."
          : "We could not log you in. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <Link href="/" className="block text-center font-bold text-lg mb-8">
          Campus Support
        </Link>
        <form onSubmit={onSubmit} className="panel space-y-5">
          <div>
            <h1 className="text-2xl font-bold">Log in</h1>
            <p className="text-sm text-[rgba(238,243,255,0.6)] mt-1">
              Use the email your university gave you.
            </p>
          </div>

          <div>
            <label className="label" htmlFor="email">University email</label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@uonbi.ac.ke"
            />
          </div>

          <div>
            <label className="label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <div className="alert-error">{error}</div>}

          <button type="submit" disabled={busy} className="btn btn-primary w-full disabled:opacity-60">
            {busy ? "Logging in…" : "Log in"}
          </button>

          <p className="text-sm text-center text-[rgba(238,243,255,0.6)]">
            New here?{" "}
            <Link href="/register" className="text-[#6FC8FF] hover:underline">
              Create an account
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
