"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import { api, ApiError, saveTokens, type TokenPair, type University } from "@/lib/api";

const ERROR_TEXT: Record<string, string> = {
  email_domain_not_allowed: "Please use the university email address for the campus you selected.",
  email_already_registered: "An account with this email already exists. Try logging in.",
  university_not_found: "That university is not available. Choose another one.",
};

export default function RegisterPage() {
  const router = useRouter();
  const [universities, setUniversities] = useState<University[]>([]);
  const [universityId, setUniversityId] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<University[]>("/universities")
      .then(setUniversities)
      .catch(() => setError("Could not load the list of universities."));
  }, []);

  const selected = universities.find((u) => u.id === universityId);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const tokens = await api<TokenPair>("/auth/register", {
        method: "POST",
        json: { email, password, full_name: fullName || null, university_id: universityId },
      });
      saveTokens(tokens);
      router.replace("/onboarding");
    } catch (err) {
      const code = err instanceof ApiError ? err.detail : "";
      setError(ERROR_TEXT[code] ?? "We could not create your account. Please try again.");
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
            <h1 className="text-2xl font-bold">Create your account</h1>
            <p className="text-sm text-[rgba(238,243,255,0.6)] mt-1">
              Students sign up with their university email. Counsellors are added by their campus admin.
            </p>
          </div>

          <div>
            <label className="label" htmlFor="university">University</label>
            <select
              id="university"
              required
              className="input"
              value={universityId}
              onChange={(e) => setUniversityId(e.target.value)}
            >
              <option value="" disabled>
                Select your university
              </option>
              {universities.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label" htmlFor="name">Full name</label>
            <input
              id="name"
              className="input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoComplete="name"
            />
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
              placeholder={selected ? `name@${selected.domains[0]}` : "name@university.ac.ke"}
            />
          </div>

          <div>
            <label className="label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              maxLength={72}
              autoComplete="new-password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <p className="text-xs text-[rgba(238,243,255,0.5)] mt-1">At least 8 characters.</p>
          </div>

          {error && <div className="alert-error">{error}</div>}

          <button
            type="submit"
            disabled={busy || !universityId}
            className="btn btn-primary w-full disabled:opacity-60"
          >
            {busy ? "Creating account…" : "Create account"}
          </button>

          <p className="text-sm text-center text-[rgba(238,243,255,0.6)]">
            Already have an account?{" "}
            <Link href="/login" className="text-[#6FC8FF] hover:underline">
              Log in
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
