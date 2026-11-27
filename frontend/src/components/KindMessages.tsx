"use client";

import { useEffect, useState, type FormEvent } from "react";

import { api, ApiError, formatDateTime, type KindNote, type KindTheme } from "@/lib/api";

const THEMES: { key: KindTheme; label: string }[] = [
  { key: "encouragement", label: "Encouragement" },
  { key: "hope", label: "Hope" },
  { key: "rest", label: "Rest" },
  { key: "self_kindness", label: "Self-kindness" },
];

type Tab = "message" | "note";

export default function KindMessages() {
  const [tab, setTab] = useState<Tab>("message");

  return (
    <aside className="panel space-y-5 lg:sticky lg:top-24">
      <div>
        <h2 className="font-semibold">Kind words</h2>
        <p className="mt-1 text-sm text-[rgb(var(--fg)/0.6)]">
          Get a short message to lift your mood, or write something nice for someone else.
        </p>
      </div>

      <div className="flex gap-5 border-b border-[rgb(var(--fg)/0.15)]" role="tablist">
        {(
          [
            ["message", "A kind message"],
            ["note", "Write to someone"],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            onClick={() => setTab(key)}
            className={`-mb-px border-b-2 pb-2 text-sm font-semibold transition-colors ${
              tab === key
                ? "border-[rgb(var(--accent))] text-[rgb(var(--fg))]"
                : "border-transparent text-[rgb(var(--fg)/0.5)] hover:text-[rgb(var(--fg))]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "message" ? <MessagePanel /> : <NotesPanel />}
    </aside>
  );
}

function MessagePanel() {
  const [theme, setTheme] = useState<KindTheme>("encouragement");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function generate() {
    setBusy(true);
    setError(null);
    setCopied(false);
    try {
      const result = await api<{ message: string }>("/kindness/message", {
        method: "POST",
        json: { theme },
      });
      setMessage(result.message);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 503
          ? "Kind messages are not available right now. You can still write a note to someone."
          : "Could not get a message. Try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
    } catch {
      setError("Copying is blocked in this browser. Select the text and copy it instead.");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {THEMES.map((t) => (
          <button
            key={t.key}
            type="button"
            aria-pressed={theme === t.key}
            onClick={() => setTheme(t.key)}
            className={`rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
              theme === t.key
                ? "border-[rgb(var(--accent))] bg-[rgb(var(--accent))] text-white"
                : "border-[rgb(var(--fg)/0.2)] text-[rgb(var(--fg)/0.75)] hover:border-[rgb(var(--link))]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <button type="button" onClick={generate} disabled={busy} className="btn btn-primary w-full text-sm disabled:opacity-60">
        {busy ? "Writing…" : message ? "Another message" : "Get a kind message"}
      </button>

      {message && (
        <div className="space-y-3 rounded-xl border border-[rgb(var(--link)/0.3)] bg-[rgb(var(--accent)/0.08)] p-4">
          <p className="text-[0.95rem] leading-relaxed">{message}</p>
          <button type="button" onClick={() => copy(message)} className="text-xs font-semibold text-[rgb(var(--link))] hover:underline">
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      )}

      {error && <div className="alert-error">{error}</div>}
    </div>
  );
}

function NotesPanel() {
  const [notes, setNotes] = useState<KindNote[]>([]);
  const [recipient, setRecipient] = useState("");
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    api<KindNote[]>("/kindness/notes")
      .then((list) => {
        if (active) setNotes(list);
      })
      .catch(() => {
        if (active) setError("Could not load your saved notes.");
      });
    return () => {
      active = false;
    };
  }, [attempt]);

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api<KindNote>("/kindness/notes", {
        method: "POST",
        json: { recipient: recipient.trim() || null, body: body.trim() },
      });
      setRecipient("");
      setBody("");
      setAttempt((n) => n + 1);
    } catch {
      setError("Could not save your note. Try again.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await api(`/kindness/notes/${id}`, { method: "DELETE" });
      setNotes((list) => list.filter((n) => n.id !== id));
    } catch {
      setError("Could not delete that note.");
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={save} className="space-y-3">
        <input
          className="input"
          maxLength={120}
          placeholder="To (optional), e.g. Mum, my friend Wanjiku"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
        />
        <textarea
          className="input min-h-28 resize-y"
          maxLength={2000}
          required
          placeholder="Write something nice. A thank you, a memory, a word of encouragement."
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
        <button type="submit" disabled={busy || !body.trim()} className="btn btn-primary w-full text-sm disabled:opacity-60">
          {busy ? "Saving…" : "Save note"}
        </button>
      </form>

      {error && <div className="alert-error">{error}</div>}

      {notes.length > 0 && (
        <ul className="max-h-80 space-y-3 overflow-y-auto pr-1">
          {notes.map((n) => (
            <li key={n.id} className="rounded-xl border border-[rgb(var(--fg)/0.12)] p-3">
              <div className="flex items-center justify-between gap-2 text-xs text-[rgb(var(--fg)/0.55)]">
                <span>{n.recipient ? `To ${n.recipient}` : "Note"}</span>
                <span>{formatDateTime(n.created_at)}</span>
              </div>
              <p className="mt-2 whitespace-pre-wrap text-sm">{n.body}</p>
              <div className="mt-2 flex gap-3 text-xs">
                <button type="button" onClick={() => navigator.clipboard.writeText(n.body)} className="font-semibold text-[rgb(var(--link))] hover:underline">
                  Copy
                </button>
                <button type="button" onClick={() => remove(n.id)} className="font-semibold text-[rgb(var(--danger))] hover:underline">
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
