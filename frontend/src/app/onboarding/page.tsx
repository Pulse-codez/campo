"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import AppShell, { useUser } from "@/components/AppShell";
import ProfileFields, { type ProfileValues } from "@/components/ProfileFields";
import { api, ApiError, type ConsentItem, type ConsentScope, type User } from "@/lib/api";

const SCOPE_COPY: Record<ConsentScope, { title: string; detail: string }> = {
  counselling: {
    title: "Counselling",
    detail: "Lets a campus counsellor see your requests and summaries so they can support you. Required to book a session.",
  },
  emergency_contact: {
    title: "Emergency contact",
    detail: "Lets us notify the person you name if we believe you are in danger. Only with this consent.",
  },
  research: {
    title: "Research",
    detail: "Allows de-identified conversation data to be used for research approved by the campus counselling unit.",
  },
  analytics: {
    title: "Aggregate analytics",
    detail: "Allows weekly, anonymous counts to help the campus improve services. Never shown per student.",
  },
};

const DEFAULTS: Record<ConsentScope, boolean> = {
  counselling: false,
  emergency_contact: false,
  research: false,
  analytics: false,
};

export default function OnboardingPage() {
  return (
    <AppShell>
      <OnboardingForm />
    </AppShell>
  );
}

function OnboardingForm() {
  const router = useRouter();
  const user: User = useUser();
  const [consents, setConsents] = useState<Record<ConsentScope, boolean>>(DEFAULTS);
  const [profile, setProfile] = useState<ProfileValues>({
    gender: user.gender ?? "",
    year_of_study: user.year_of_study ? String(user.year_of_study) : "",
    field_of_study: user.field_of_study ?? "other",
    voice_preference: user.voice_preference ?? "auto",
  });
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [acknowledged, setAcknowledged] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!user.onboarded) return;
    api<ConsentItem[]>("/consents/me").then((items) => {
      const next = { ...DEFAULTS };
      items.forEach((i) => {
        next[i.scope] = i.granted;
      });
      setConsents(next);
    });
  }, [user.onboarded]);

  function toggle(scope: ConsentScope) {
    setConsents((c) => ({ ...c, [scope]: !c[scope] }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!acknowledged) {
      setError("Please read and confirm how your data is used.");
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
          consents,
          gender: profile.gender || null,
          year_of_study: profile.year_of_study ? Number(profile.year_of_study) : null,
          field_of_study: profile.field_of_study,
          voice_preference: profile.voice_preference,
          emergency_contact_name: consents.emergency_contact ? contactName.trim() : null,
          emergency_contact_phone: consents.emergency_contact ? contactPhone.trim() : null,
          policy_version: "v1.0",
        },
      });
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not save your choices. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold">
          {user.onboarded ? "Your privacy choices" : `Welcome, ${user.full_name ?? "student"}`}
        </h1>
        <p className="text-[rgba(238,243,255,0.65)] mt-2">
          You choose what we share and with whom. You can change any choice later, and changes take
          effect straight away. Nothing here turns off access to support.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-6">
        <section className="space-y-3">
          {(Object.keys(SCOPE_COPY) as ConsentScope[]).map((scope) => (
            <label key={scope} className="panel flex gap-4 cursor-pointer">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 accent-[#1B4FD8]"
                checked={consents[scope]}
                onChange={() => toggle(scope)}
              />
              <span>
                <span className="block font-semibold">{SCOPE_COPY[scope].title}</span>
                <span className="block text-sm text-[rgba(238,243,255,0.6)] mt-1">
                  {SCOPE_COPY[scope].detail}
                </span>
              </span>
            </label>
          ))}
        </section>

        {consents.emergency_contact && (
          <section className="panel space-y-4">
            <h2 className="font-semibold">Emergency contact</h2>
            <div>
              <label className="label" htmlFor="contact-name">Name</label>
              <input
                id="contact-name"
                className="input"
                value={contactName}
                onChange={(e) => setContactName(e.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="contact-phone">Phone</label>
              <input
                id="contact-phone"
                type="tel"
                className="input"
                value={contactPhone}
                onChange={(e) => setContactPhone(e.target.value)}
                placeholder="+254…"
              />
            </div>
          </section>
        )}

        <ProfileFields values={profile} onChange={setProfile} />

        <label className="panel flex gap-4 cursor-pointer">
          <input
            type="checkbox"
            className="mt-1 h-4 w-4 accent-[#1B4FD8]"
            checked={acknowledged}
            onChange={(e) => setAcknowledged(e.target.checked)}
          />
          <span className="text-sm text-[rgba(238,243,255,0.8)]">
            I understand what is recorded, why, and how long it is kept. Conversations are kept under
            the campus retention policy. Voice audio is discarded after transcription unless I opt in.
          </span>
        </label>

        {error && <div className="alert-error">{error}</div>}

        <button type="submit" disabled={busy} className="btn btn-primary w-full disabled:opacity-60">
          {busy ? "Saving…" : user.onboarded ? "Save changes" : "Finish setup"}
        </button>
      </form>
    </div>
  );
}
