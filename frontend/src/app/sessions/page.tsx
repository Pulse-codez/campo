"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type FormEvent } from "react";

import AppShell, { useUser } from "@/components/AppShell";
import StatusPill from "@/components/StatusPill";
import {
  api,
  ApiError,
  formatDateTime,
  type ConsentItem,
  type CounsellingSession,
  type SessionStatus,
} from "@/lib/api";

export default function SessionsPage() {
  return (
    <AppShell>
      <SessionsContent />
    </AppShell>
  );
}

function SessionsContent() {
  const user = useUser();
  const isStudent = user.role === "student";
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">{isStudent ? "Counselling sessions" : "Session queue"}</h1>
        <p className="text-[rgb(var(--fg)/0.6)] mt-2">
          {isStudent
            ? "Request time with a campus counsellor or peer counsellor. Requests are private to you and the team you are matched with."
            : "Students from your university who have consented to counselling. Accept a request to take it on."}
        </p>
      </div>
      {isStudent ? <StudentView /> : <StaffQueue />}
    </div>
  );
}

function StudentView() {
  const [sessions, setSessions] = useState<CounsellingSession[]>([]);
  const [consented, setConsented] = useState<boolean | null>(null);
  const [topic, setTopic] = useState("");
  const [preferred, setPreferred] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const fetchAll = useCallback(
    () =>
      Promise.all([
        api<CounsellingSession[]>("/counselling-sessions"),
        api<ConsentItem[]>("/consents/me"),
      ]),
    [],
  );

  const apply = useCallback(([list, items]: [CounsellingSession[], ConsentItem[]]) => {
    setSessions(list);
    setConsented(items.some((i) => i.scope === "counselling" && i.granted));
  }, []);

  useEffect(() => {
    fetchAll().then(apply);
  }, [fetchAll, apply]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api("/counselling-sessions", {
        method: "POST",
        json: { topic, preferred_time: preferred || null },
      });
      setTopic("");
      setPreferred("");
      apply(await fetchAll());
    } catch (err) {
      setError(
        err instanceof ApiError && err.detail === "counselling_consent_required"
          ? "Turn on counselling consent in your privacy choices to request a session."
          : "Could not send your request. Try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid lg:grid-cols-5 gap-8">
      <section className="lg:col-span-2">
        {consented === false ? (
          <div className="panel space-y-3">
            <h2 className="font-semibold">Counselling consent is off</h2>
            <p className="text-sm text-[rgb(var(--fg)/0.65)]">
              Counsellors only see requests from students who have chosen to share with them.
            </p>
            <Link href="/onboarding" className="btn btn-outline text-sm px-4 py-2 inline-flex">
              Review privacy choices
            </Link>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="panel space-y-4">
            <h2 className="font-semibold">Request a session</h2>
            <div>
              <label className="label" htmlFor="topic">What would you like to talk about?</label>
              <input
                id="topic"
                required
                maxLength={255}
                className="input"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. exam stress, sleep, family pressure"
              />
            </div>
            <div>
              <label className="label" htmlFor="preferred">Preferred time (optional)</label>
              <input
                id="preferred"
                maxLength={255}
                className="input"
                value={preferred}
                onChange={(e) => setPreferred(e.target.value)}
                placeholder="e.g. weekday afternoons"
              />
            </div>
            {error && <div className="alert-error">{error}</div>}
            <button type="submit" disabled={busy} className="btn btn-primary w-full disabled:opacity-60">
              {busy ? "Sending…" : "Send request"}
            </button>
          </form>
        )}
      </section>

      <section className="lg:col-span-3 space-y-3">
        <h2 className="font-semibold">Your requests</h2>
        {sessions.length === 0 ? (
          <p className="text-sm text-[rgb(var(--fg)/0.55)]">No requests yet.</p>
        ) : (
          sessions.map((s) => (
            <div key={s.id} className="panel flex flex-wrap justify-between gap-3">
              <div>
                <p className="font-semibold">{s.topic}</p>
                <p className="text-sm text-[rgb(var(--fg)/0.55)]">
                  {s.preferred_time ? `${s.preferred_time} · ` : ""}Sent {formatDateTime(s.created_at)}
                </p>
              </div>
              <StatusPill status={s.status} />
            </div>
          ))
        )}
      </section>
    </div>
  );
}

const NEXT_ACTIONS: Record<SessionStatus, { label: string; to: SessionStatus }[]> = {
  requested: [
    { label: "Accept", to: "booked" },
    { label: "Cancel", to: "cancelled" },
  ],
  booked: [
    { label: "Mark completed", to: "completed" },
    { label: "Cancel", to: "cancelled" },
  ],
  completed: [],
  cancelled: [],
};

function StaffQueue() {
  const [sessions, setSessions] = useState<CounsellingSession[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchQueue = useCallback(() => api<CounsellingSession[]>("/counselling-sessions"), []);

  useEffect(() => {
    fetchQueue().then(setSessions);
  }, [fetchQueue]);

  async function move(session: CounsellingSession, status: SessionStatus) {
    setError(null);
    try {
      await api(`/counselling-sessions/${session.id}`, { method: "PATCH", json: { status } });
      setSessions(await fetchQueue());
    } catch {
      setError("Could not update this session. It may have been taken by another counsellor.");
    }
  }

  if (sessions.length === 0) {
    return <p className="text-sm text-[rgb(var(--fg)/0.55)]">Nothing in the queue right now.</p>;
  }

  return (
    <div className="space-y-3">
      {error && <div className="alert-error">{error}</div>}
      {sessions.map((s) => (
        <div key={s.id} className="panel flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-semibold">{s.topic}</p>
            <p className="text-sm text-[rgb(var(--fg)/0.6)]">
              {s.student_name ?? "Student"}
              {s.preferred_time ? ` · ${s.preferred_time}` : ""} · {formatDateTime(s.created_at)}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <StatusPill status={s.status} />
            {NEXT_ACTIONS[s.status].map((action) => (
              <button
                key={action.label}
                onClick={() => move(s, action.to)}
                className="btn btn-outline text-sm px-3 py-1.5"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
