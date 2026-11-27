"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState, type FormEvent } from "react";

import ProfileFields, { type ProfileValues } from "@/components/ProfileFields";
import SplitLayout, { Emblem, BrandMark } from "@/components/auth/SplitLayout";
import {
  AUTH_BUTTON,
  AUTH_BUTTON_OUTLINE,
  AUTH_ERROR,
  AUTH_INPUT,
  AUTH_LABEL,
  AUTH_NOTICE,
} from "@/components/auth/styles";
import { destinationFor } from "@/lib/useAuth";
import { apiBase, api, ApiError, getUniversities, saveTokens, type TokenPair, type University, type User } from "@/lib/api";

type Tab = "signin" | "new";

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginContent />
    </Suspense>
  );
}

function LoginContent() {
  const params = useSearchParams();
  const [tab, setTab] = useState<Tab>(params.get("tab") === "new" ? "new" : "signin");
  const [notice, setNotice] = useState<string | null>(null);
  const [prefillEmail, setPrefillEmail] = useState("");

  return (
    <SplitLayout left={<LeftPanel />}>
      <div className="w-full max-w-sm">
        <p className="text-[11px] font-semibold tracking-[0.2em] text-[rgb(var(--fg)/0.62)]">CAMPUS SUPPORT / STUDENT ACCESS</p>
        <h1 className="mt-3 text-4xl font-bold text-[rgb(var(--fg))]">
          {tab === "signin" ? "Welcome back." : "Create your account."}
        </h1>
        <p className="mt-2 text-[rgb(var(--fg)/0.62)]">
          {tab === "signin"
            ? "Sign in with your university email to continue."
            : "Use the university email your campus issued to you."}
        </p>

        <div className="mt-8 flex gap-6 border-b border-[rgb(var(--fg)/0.15)]" role="tablist">
          {(
            [
              ["signin", "Sign in"],
              ["new", "New student"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              role="tab"
              aria-selected={tab === key}
              onClick={() => {
                setTab(key);
                setNotice(null);
              }}
              className={`-mb-px pb-3 text-sm font-semibold transition-colors ${
                tab === key
                  ? "border-b-2 border-[rgb(var(--accent))] text-[rgb(var(--fg))]"
                  : "border-b-2 border-transparent text-[rgb(var(--fg)/0.45)] hover:text-[rgb(var(--fg))]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="mt-6 space-y-5">
          {notice && <div className={AUTH_NOTICE}>{notice}</div>}
          {tab === "signin" ? (
            <SignInForm key={prefillEmail} prefillEmail={prefillEmail} />
          ) : (
            <SignUpForm
              onCreated={(email) => {
                setPrefillEmail(email);
                setNotice("Your account is ready. Sign in to continue.");
                setTab("signin");
              }}
            />
          )}
        </div>

        <div className="mt-8 space-y-3">
          <p className="text-center text-xs text-[rgb(var(--fg)/0.45)]">or</p>
          <Link href="/help" className={AUTH_BUTTON_OUTLINE + " block"}>
            Get urgent help without an account
          </Link>
        </div>
        <p className="mt-8 text-center text-xs text-[rgb(var(--fg)/0.45)]">
          Confidential · Only your university email can create an account · Not an emergency service
        </p>
      </div>
    </SplitLayout>
  );
}

function SignInForm({ prefillEmail }: { prefillEmail: string }) {
  const router = useRouter();
  const [email, setEmail] = useState(prefillEmail);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const tokens = await api<TokenPair>("/auth/login", { method: "POST", json: { email, password } });
      saveTokens(tokens);
      const me = await api<User>("/auth/me");
      router.replace(destinationFor(me));
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? "That email and password don't match. Check them and try again."
          : "We could not sign you in. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5">
      <div>
        <label className={AUTH_LABEL} htmlFor="email">University email</label>
        <input
          id="email"
          type="email"
          required
          autoComplete="email"
          className={AUTH_INPUT}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@uonbi.ac.ke"
        />
      </div>
      <div>
        <label className={AUTH_LABEL} htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          required
          autoComplete="current-password"
          className={AUTH_INPUT}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      {error && <div className={AUTH_ERROR}>{error}</div>}
      <button type="submit" disabled={busy} className={AUTH_BUTTON}>
        {busy ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}

const SIGNUP_ERRORS: Record<string, string> = {
  email_domain_not_allowed: "Use the university email address for the campus you selected.",
  other_university_name_required: "Type the name of your university.",
  other_email_not_accepted: "For an unlisted university, use your academic email (ending in .ac.ke or .edu).",
  email_already_registered: "An account with this email already exists. Sign in instead.",
  university_not_found: "That university is not available. Choose another one.",
};

function loadErrorText(err: unknown): string {
  if (err instanceof ApiError && err.status === 0) {
    return `Cannot reach the server at ${apiBase()}. Check that the backend is running, then try again.`;
  }
  return "We could not load the list of universities. Try again.";
}

function SignUpForm({ onCreated }: { onCreated: (email: string) => void }) {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [universityId, setUniversityId] = useState("");
  const [otherName, setOtherName] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [profile, setProfile] = useState<ProfileValues>({
    gender: "",
    year_of_study: "",
    field_of_study: "other",
    voice_preference: "auto",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    getUniversities(attempt > 0)
      .then((list) => {
        if (active) setUniversities(list);
      })
      .catch((err) => {
        if (active) setLoadError(loadErrorText(err));
      });
    return () => {
      active = false;
    };
  }, [attempt]);

  function retry() {
    setLoadError(null);
    setAttempt((n) => n + 1);
  }

  const selected = universities.find((u) => u.id === universityId);
  const isOther = selected?.slug === "other";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      // The sign-up response carries tokens. They are not stored: students sign in on the next step.
      await api<TokenPair>("/auth/register", {
        method: "POST",
        json: {
          email,
          password,
          full_name: fullName || null,
          university_id: universityId,
          other_university_name: isOther ? otherName.trim() : null,
          gender: profile.gender || null,
          year_of_study: profile.year_of_study ? Number(profile.year_of_study) : null,
          field_of_study: profile.field_of_study,
          voice_preference: profile.voice_preference,
        },
      });
      onCreated(email);
    } catch (err) {
      const code = err instanceof ApiError ? err.detail : "";
      setError(
        err instanceof ApiError && err.status === 0
          ? loadErrorText(err)
          : (SIGNUP_ERRORS[code] ?? "We could not create your account. Please try again."),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5">
      <div>
        <label className={AUTH_LABEL} htmlFor="university">University</label>
        <select
          id="university"
          required
          className={AUTH_INPUT}
          value={universityId}
          onChange={(e) => setUniversityId(e.target.value)}
          disabled={universities.length === 0}
        >
          <option value="" disabled>
            {universities.length === 0 && !loadError ? "Loading universities…" : "Select your university"}
          </option>
          {universities.map((u) => (
            <option key={u.id} value={u.id}>{u.name}</option>
          ))}
        </select>
        {loadError && (
          <div className={AUTH_ERROR + " mt-2 flex items-center justify-between gap-3"}>
            <span>{loadError}</span>
            <button type="button" onClick={retry} className="shrink-0 font-semibold underline">
              Try again
            </button>
          </div>
        )}
      </div>
      {isOther && (
        <div>
          <label className={AUTH_LABEL} htmlFor="other-name">Your university</label>
          <input
            id="other-name"
            required
            maxLength={255}
            className={AUTH_INPUT}
            value={otherName}
            onChange={(e) => setOtherName(e.target.value)}
            placeholder="e.g. Mount Kenya University"
          />
          <p className="mt-1.5 text-xs text-[rgb(var(--fg)/0.45)]">
            For an unlisted university, use your academic email (ending in .ac.ke or .edu).
          </p>
        </div>
      )}
      <div>
        <label className={AUTH_LABEL} htmlFor="name">Full name</label>
        <input id="name" className={AUTH_INPUT} value={fullName} onChange={(e) => setFullName(e.target.value)} autoComplete="name" />
      </div>
      <div>
        <label className={AUTH_LABEL} htmlFor="signup-email">University email</label>
        <input
          id="signup-email"
          type="email"
          required
          autoComplete="email"
          className={AUTH_INPUT}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={isOther || !selected ? "you@university.ac.ke" : `you@${selected.domains[0]}`}
        />
      </div>
      <div>
        <label className={AUTH_LABEL} htmlFor="signup-password">Password</label>
        <input
          id="signup-password"
          type="password"
          required
          minLength={8}
          maxLength={72}
          autoComplete="new-password"
          className={AUTH_INPUT}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <p className="mt-1.5 text-xs text-[rgb(var(--fg)/0.45)]">At least 8 characters.</p>
      </div>
      <ProfileFields values={profile} onChange={setProfile} />
      {error && <div className={AUTH_ERROR}>{error}</div>}
      <button type="submit" disabled={busy || !universityId} className={AUTH_BUTTON}>
        {busy ? "Creating account…" : "Create account"}
      </button>
    </form>
  );
}

function LeftPanel() {
  return (
    <>
      <BrandMark />
      <p className="mt-16 text-[11px] font-semibold tracking-[0.2em] text-[rgb(var(--fg)/0.62)]">A PRIVATE SPACE FOR STUDENTS</p>
      <h2 className="mt-4 text-6xl leading-[1.02] text-[rgb(var(--fg))]" style={{ fontFamily: "Georgia, serif" }}>
        You don&apos;t have
        <br />
        to carry it
        <br />
        <em className="text-[rgb(var(--link))]">alone.</em>
      </h2>
      <p className="mt-6 max-w-md text-[15px] leading-relaxed text-[rgb(var(--fg)/0.62)]">
        Always-on conversation, coping tools, and a route to a campus counsellor when you need a person.
      </p>
      <div className="mt-auto flex justify-center pt-12">
        <Emblem />
      </div>
    </>
  );
}
