"use client";

import { useEffect, useState, type FormEvent } from "react";

import AppShell from "@/components/AppShell";
import { AUTH_BUTTON, AUTH_ERROR, AUTH_INPUT, AUTH_LABEL } from "@/components/auth/styles";
import { api, ApiError, type CheckinEntry, type CheckinResult, type CheckinStatus } from "@/lib/api";

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

function monthLabel(period: string): string {
  const [year, month] = period.split("-").map(Number);
  return `${MONTHS[month - 1]} ${year}`;
}

export default function CheckinPage() {
  return (
    <AppShell>
      <CheckinContent />
    </AppShell>
  );
}

function CheckinContent() {
  const [status, setStatus] = useState<CheckinStatus | null>(null);
  const [entries, setEntries] = useState<CheckinEntry[]>([]);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    Promise.all([api<CheckinStatus>("/checkin/status"), api<CheckinEntry[]>("/checkin")]).then(([s, list]) => {
      if (!active) return;
      setStatus(s);
      setEntries(list);
    });
    return () => {
      active = false;
    };
  }, [attempt]);

  return (
    <div className="mx-auto max-w-3xl space-y-10">
      <div>
        <p className="text-[11px] font-semibold tracking-[0.2em] text-[rgb(var(--fg)/0.5)]">MONTHLY CHECK-IN</p>
        <h1 className="mt-2 text-3xl font-bold">How are you doing this month?</h1>
        <p className="mt-2 text-[rgb(var(--fg)/0.62)]">
          Once a month, take a few minutes to write about how you are feeling and where you are heading. Only you
          can read these.
        </p>
      </div>

      {status && status.open_periods.length > 0 ? (
        <CheckinForm
          periods={status.open_periods}
          onSaved={() => setAttempt((n) => n + 1)}
        />
      ) : (
        <div className="panel space-y-2">
          <h2 className="font-semibold">Nothing to write right now</h2>
          <p className="text-sm text-[rgb(var(--fg)/0.65)]">
            Check-ins open in the last seven days of each month. You can still write for any of the last three months
            you missed.
          </p>
        </div>
      )}

      <section className="space-y-4">
        <h2 className="font-semibold">Your past check-ins</h2>
        {entries.length === 0 ? (
          <p className="text-sm text-[rgb(var(--fg)/0.55)]">Your check-ins will appear here.</p>
        ) : (
          entries.map((e) => (
            <article key={e.id} className="panel space-y-4">
              <h3 className="font-semibold">{monthLabel(e.period)}</h3>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-[rgb(var(--fg)/0.5)]">How I am feeling</p>
                <p className="mt-1 whitespace-pre-wrap text-sm">{e.feelings}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-[rgb(var(--fg)/0.5)]">Where I am going</p>
                <p className="mt-1 whitespace-pre-wrap text-sm">{e.direction}</p>
              </div>
            </article>
          ))
        )}
      </section>
    </div>
  );
}

function CheckinForm({ periods, onSaved }: { periods: string[]; onSaved: () => void }) {
  const [period, setPeriod] = useState(periods[0]);
  const [feelings, setFeelings] = useState("");
  const [direction, setDirection] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [crisis, setCrisis] = useState<string[] | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await api<CheckinResult>("/checkin", {
        method: "POST",
        json: { period, feelings: feelings.trim(), direction: direction.trim() },
      });
      setFeelings("");
      setDirection("");
      if (result.requires_human) setCrisis(result.contacts);
      onSaved();
    } catch (err) {
      setError(
        err instanceof ApiError && err.detail === "already_submitted"
          ? "You have already written a check-in for this month."
          : "Could not save your check-in. Try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="panel space-y-5">
      {crisis && (
        <div className="alert-crisis space-y-2">
          <p className="font-semibold">Your check-in is saved. If you are in danger, reach someone now.</p>
          <ul className="space-y-1 text-sm">
            {crisis.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <label className={AUTH_LABEL} htmlFor="period">Month</label>
        <select id="period" className={AUTH_INPUT} value={period} onChange={(e) => setPeriod(e.target.value)}>
          {periods.map((p) => (
            <option key={p} value={p}>{monthLabel(p)}</option>
          ))}
        </select>
      </div>

      <div>
        <label className={AUTH_LABEL} htmlFor="feelings">How are you feeling this month?</label>
        <textarea
          id="feelings"
          required
          maxLength={4000}
          rows={5}
          className={AUTH_INPUT}
          value={feelings}
          onChange={(e) => setFeelings(e.target.value)}
          placeholder="Tired, hopeful, lonely, proud. Write as much or as little as you like."
        />
      </div>

      <div>
        <label className={AUTH_LABEL} htmlFor="direction">Where are you going in life?</label>
        <textarea
          id="direction"
          required
          maxLength={4000}
          rows={5}
          className={AUTH_INPUT}
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          placeholder="The next step, a dream, something you want to let go of."
        />
      </div>

      {error && <div className={AUTH_ERROR}>{error}</div>}

      <button type="submit" disabled={busy || !feelings.trim() || !direction.trim()} className={AUTH_BUTTON}>
        {busy ? "Saving…" : "Save check-in"}
      </button>
    </form>
  );
}
