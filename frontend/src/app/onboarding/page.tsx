"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import SplitLayout, { BrandMark, Emblem } from "@/components/auth/SplitLayout";
import { AUTH_BUTTON, AUTH_BUTTON_OUTLINE, AUTH_ERROR, AUTH_INPUT, AUTH_LABEL } from "@/components/auth/styles";
import {
  api,
  ApiError,
  type Concern,
  type ConsentItem,
  type ConsentScope,
  type Recommendation,
  type Therapist,
  type User,
} from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

const CONSENT_COPY: Record<ConsentScope, { title: string; detail: string }> = {
  counselling: {
    title: "Share with my campus counsellor",
    detail: "Lets a counsellor at my university see my counselling requests and summaries. Needed to book a session.",
  },
  emergency_contact: {
    title: "Notify my emergency contact",
    detail: "Lets the campus notify the person I name if they believe I am in danger.",
  },
  research: {
    title: "Use my de-identified data for research",
    detail: "Approved research by the campus counselling unit only. Never names me.",
  },
  analytics: {
    title: "Include me in anonymous counts",
    detail: "Weekly totals that help the campus improve services. Never shown per student.",
  },
};

const CONSENT_DEFAULTS: Record<ConsentScope, boolean> = {
  counselling: false,
  emergency_contact: false,
  research: false,
  analytics: false,
};

const STEP_TITLES = [
  { title: "What's on your mind?", sub: "Pick everything that applies. We use this to suggest the right virtual therapist." },
  { title: "Choose your virtual therapist.", sub: "A companion for the conversation. You can change it later." },
  { title: "Your privacy, your choice.", sub: "You decide what is shared. Changes take effect straight away." },
];

export default function OnboardingPage() {
  const { user, loading } = useAuth();

  if (loading || !user) {
    return <div className="min-h-screen flex items-center justify-center bg-[rgb(var(--surface))] text-[rgb(var(--fg)/0.62)]">Loading…</div>;
  }
  if (user.role !== "student") {
    return (
      <SplitLayout left={<LeftPanel step={0} />}>
        <div className="w-full max-w-md space-y-4">
          <h1 className="text-3xl font-bold">Staff accounts don&apos;t need onboarding.</h1>
          <p className="text-[rgb(var(--fg)/0.62)]">Head to the session queue to see requests from students.</p>
          <Link href="/sessions" className={AUTH_BUTTON + " inline-block text-center"}>Open the queue</Link>
        </div>
      </SplitLayout>
    );
  }
  return <OnboardingFlow key={user.id} user={user} />;
}

function OnboardingFlow({ user }: { user: User }) {
  const router = useRouter();
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [concernOptions, setConcernOptions] = useState<Concern[]>([]);
  const [therapists, setTherapists] = useState<Therapist[]>([]);
  const [concerns, setConcerns] = useState<string[]>(user.concerns);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [therapistKey, setTherapistKey] = useState<string | null>(user.therapist_key);
  const [consents, setConsents] = useState<Record<ConsentScope, boolean>>(CONSENT_DEFAULTS);
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [acknowledged, setAcknowledged] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<Concern[]>("/concerns").then(setConcernOptions).catch(() => setError("Could not load the list."));
    api<Therapist[]>("/therapists").then(setTherapists);
    if (concerns.length) {
      api<Recommendation>("/therapists/recommend", { method: "POST", json: { concerns } }).then(setRecommendation);
    }
    if (user.onboarded) {
      api<ConsentItem[]>("/consents/me").then((items) => {
        const next = { ...CONSENT_DEFAULTS };
        items.forEach((i) => {
          next[i.scope] = i.granted;
        });
        setConsents(next);
      });
    }
    // Only on mount: the form starts from the user's saved choices.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const showCrisis = concerns.includes("suicide");

  function toggleConcern(key: string) {
    const next = concerns.includes(key) ? concerns.filter((c) => c !== key) : [...concerns, key];
    setConcerns(next);
    if (next.length === 0) {
      setRecommendation(null);
      return;
    }
    api<Recommendation>("/therapists/recommend", { method: "POST", json: { concerns: next } }).then((rec) => {
      setRecommendation(rec);
      setTherapistKey((current) => current ?? rec.primary.key);
    });
  }

  function toggleConsent(scope: ConsentScope) {
    setConsents((c) => ({ ...c, [scope]: !c[scope] }));
  }

  async function finish(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!acknowledged) {
      setError("Please confirm how your data is used.");
      return;
    }
    if (consents.emergency_contact && (!contactName.trim() || !contactPhone.trim())) {
      setError("Add a name and phone number for your emergency contact, or switch that option off.");
      return;
    }
    setBusy(true);
    try {
      await api("/onboarding", {
        method: "POST",
        json: {
          concerns,
          therapist_key: therapistKey,
          consents,
          emergency_contact_name: consents.emergency_contact ? contactName.trim() : null,
          emergency_contact_phone: consents.emergency_contact ? contactPhone.trim() : null,
          policy_version: "v1.0",
        },
      });
      router.replace("/talk");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not save your choices. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <SplitLayout left={<LeftPanel step={step + 1} />}>
      <div className="w-full max-w-lg">
        <div className="mb-8 flex gap-2" aria-label={`Step ${step + 1} of 3`}>
          {[0, 1, 2].map((i) => (
            <span key={i} className={`h-1 flex-1 rounded-full ${i <= step ? "bg-[rgb(var(--accent))]" : "bg-[rgb(var(--fg)/0.15)]"}`} />
          ))}
        </div>
        <p className="text-[11px] font-semibold tracking-[0.2em] text-[rgb(var(--fg)/0.62)]">
          STEP {step + 1} OF 3 · {user.onboarded ? "PRIVACY CHOICES" : "SET UP"}
        </p>
        <h1 className="mt-3 text-4xl font-bold">{STEP_TITLES[step].title}</h1>
        <p className="mt-2 text-[rgb(var(--fg)/0.62)]">{STEP_TITLES[step].sub}</p>

        <div className="mt-8 space-y-6">
          {step === 0 && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                {concernOptions.map((c) => {
                  const on = concerns.includes(c.key);
                  return (
                    <button
                      key={c.key}
                      type="button"
                      aria-pressed={on}
                      onClick={() => toggleConcern(c.key)}
                      className={`flex items-center gap-3 rounded-xl border px-4 py-4 text-left text-sm font-semibold transition-colors ${
                        on
                          ? "border-[rgb(var(--accent))] bg-[rgb(var(--accent)/0.12)] text-[rgb(var(--fg))]"
                          : "border-[rgb(var(--fg)/0.15)] bg-[rgb(var(--surface))] text-[rgb(var(--fg))] hover:border-[rgb(var(--link)/0.5)]"
                      }`}
                    >
                      <span
                        className={`flex h-5 w-5 items-center justify-center rounded border ${
                          on ? "border-[rgb(var(--accent))] bg-[rgb(var(--accent))] text-white" : "border-[rgb(var(--fg)/0.15)]"
                        }`}
                      >
                        {on ? "✓" : ""}
                      </span>
                      {c.label}
                    </button>
                  );
                })}
              </div>
              {showCrisis && <CrisisPanel />}
              <button type="button" disabled={concerns.length === 0} onClick={() => setStep(1)} className={AUTH_BUTTON}>
                Continue
              </button>
            </>
          )}

          {step === 1 && (
            <>
              <div className="space-y-3">
                {therapists.map((t) => {
                  const selected = therapistKey === t.key;
                  const recommended = recommendation?.primary.key === t.key;
                  return (
                    <button
                      key={t.key}
                      type="button"
                      aria-pressed={selected}
                      onClick={() => setTherapistKey(t.key)}
                      className={`w-full rounded-xl border px-5 py-4 text-left transition-colors ${
                        selected ? "border-[rgb(var(--accent))] bg-[rgb(var(--accent)/0.12)]" : "border-[rgb(var(--fg)/0.15)] bg-[rgb(var(--surface))] hover:border-[rgb(var(--link)/0.5)]"
                      }`}
                    >
                      <span className="flex items-center justify-between gap-3">
                        <span className="font-semibold text-[rgb(var(--fg))]">{t.name}</span>
                        {recommended && (
                          <span className="rounded-full bg-[rgb(var(--accent))] px-2.5 py-0.5 text-[11px] font-semibold text-white">
                            Recommended
                          </span>
                        )}
                      </span>
                      <span className="mt-1 block text-sm text-[rgb(var(--fg)/0.62)]">{t.focus}</span>
                    </button>
                  );
                })}
              </div>
              <p className="rounded-lg bg-[rgb(var(--fg)/0.05)] px-4 py-3 text-xs leading-relaxed text-[rgb(var(--fg)/0.62)]">
                Virtual therapists are AI companions, not licensed clinicians. They never replace a counsellor, and a
                person is always one request away.
              </p>
              {showCrisis && <CrisisPanel />}
              <div className="flex gap-3">
                <button type="button" onClick={() => setStep(0)} className={AUTH_BUTTON_OUTLINE}>Back</button>
                <button type="button" disabled={!therapistKey} onClick={() => setStep(2)} className={AUTH_BUTTON}>
                  Continue
                </button>
              </div>
            </>
          )}

          {step === 2 && (
            <form onSubmit={finish} className="space-y-6">
              <div className="space-y-3">
                {(Object.keys(CONSENT_COPY) as ConsentScope[]).map((scope) => (
                  <label key={scope} className="flex cursor-pointer gap-3 rounded-xl border border-[rgb(var(--fg)/0.15)] bg-[rgb(var(--surface))] p-4">
                    <input
                      type="checkbox"
                      className="mt-1 h-4 w-4 accent-[rgb(var(--accent))]"
                      checked={consents[scope]}
                      onChange={() => toggleConsent(scope)}
                    />
                    <span>
                      <span className="block text-sm font-semibold">{CONSENT_COPY[scope].title}</span>
                      <span className="mt-0.5 block text-xs text-[rgb(var(--fg)/0.62)]">{CONSENT_COPY[scope].detail}</span>
                    </span>
                  </label>
                ))}
              </div>

              {consents.emergency_contact && (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className={AUTH_LABEL} htmlFor="contact-name">Contact name</label>
                    <input id="contact-name" className={AUTH_INPUT} value={contactName} onChange={(e) => setContactName(e.target.value)} />
                  </div>
                  <div>
                    <label className={AUTH_LABEL} htmlFor="contact-phone">Contact phone</label>
                    <input id="contact-phone" type="tel" className={AUTH_INPUT} value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} placeholder="+254…" />
                  </div>
                </div>
              )}

              <label className="flex cursor-pointer gap-3 text-sm text-[rgb(var(--fg))]">
                <input type="checkbox" className="mt-1 h-4 w-4 accent-[rgb(var(--accent))]" checked={acknowledged} onChange={(e) => setAcknowledged(e.target.checked)} />
                <span>
                  I understand what is recorded, why, and how long it is kept. Voice audio is discarded after
                  transcription unless I opt in.
                </span>
              </label>

              {error && <div className={AUTH_ERROR}>{error}</div>}

              <div className="flex gap-3">
                <button type="button" onClick={() => setStep(1)} className={AUTH_BUTTON_OUTLINE}>Back</button>
                <button type="submit" disabled={busy} className={AUTH_BUTTON}>
                  {busy ? "Saving…" : user.onboarded ? "Save changes" : "Start talking"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </SplitLayout>
  );
}

function CrisisPanel() {
  return (
    <div className="rounded-xl border border-[rgb(var(--danger)/0.4)] bg-[rgb(var(--danger)/0.1)] p-4 text-sm text-[rgb(var(--danger))]">
      <p className="font-semibold">If you are thinking about ending your life, reach someone now.</p>
      <ul className="mt-2 space-y-1">
        <li>National mental health helpline: <strong>1199</strong> (24/7, free)</li>
        <li>Campus security: <strong>+254 700 000 999</strong></li>
        <li>The nearest hospital emergency department</li>
      </ul>
      <p className="mt-2 text-xs">You can keep going with setup. A counsellor can also be requested from the Counselling page.</p>
    </div>
  );
}

function LeftPanel({ step }: { step: number }) {
  const copy = [
    { head: ["Let's get", "you set up."], em: "Quietly." },
    { head: ["Find a voice", "that fits."], em: "Your pace." },
    { head: ["Your data,", "your call."], em: "Always." },
  ][Math.max(0, Math.min(2, step - 1))];

  return (
    <>
      <BrandMark />
      <p className="mt-16 text-[11px] font-semibold tracking-[0.2em] text-[rgb(var(--fg)/0.62)]">A FEW MINUTES, ONCE</p>
      <h2 className="mt-4 text-6xl leading-[1.02] text-[rgb(var(--fg))]" style={{ fontFamily: "Georgia, serif" }}>
        {copy.head[0]}
        <br />
        {copy.head[1]}
        <br />
        <em className="text-[rgb(var(--link))]">{copy.em}</em>
      </h2>
      <p className="mt-6 max-w-md text-[15px] leading-relaxed text-[rgb(var(--fg)/0.62)]">
        Your answers shape the companion you talk to. Nothing here is shared with anyone on campus without your choice.
      </p>
      <div className="mt-auto flex justify-center pt-12">
        <Emblem />
      </div>
    </>
  );
}
