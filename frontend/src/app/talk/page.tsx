"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState, type FormEvent } from "react";

import AppShell, { useUser } from "@/components/AppShell";
import {
  api,
  ApiError,
  apiBlob,
  type ChatTurn,
  type Conversation,
  type Message,
  type User,
  type VoicePreference,
  type VoiceTurn,
} from "@/lib/api";

const FALLBACK_CONTACTS = [
  "National mental health helpline: 1199 (24/7, free)",
  "Campus security: +254 700 000 999 (on campus, 24/7)",
  "Nearest hospital emergency department",
];

type Bubble = { key: string; role: "user" | "assistant"; content: string };

export default function TalkPage() {
  return (
    <AppShell>
      <Suspense fallback={null}>
        <TalkConsole />
      </Suspense>
    </AppShell>
  );
}

function TalkConsole() {
  const router = useRouter();
  const params = useSearchParams();
  const user = useUser();
  const initialId = params.get("c");

  const conversationRef = useRef<string | null>(initialId);
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [crisis, setCrisis] = useState(false);
  const [contacts, setContacts] = useState<string[]>(FALLBACK_CONTACTS);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [voice, setVoice] = useState<VoicePreference>(user.voice_preference ?? "auto");

  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!initialId) return;
    api<Message[]>(`/conversations/${initialId}/messages`)
      .then((messages) =>
        setBubbles(
          messages.map((m) => ({
            key: m.id,
            role: m.role === "assistant" ? "assistant" : "user",
            content: m.content,
          })),
        ),
      )
      .catch(() => setError("Could not load this conversation."));
  }, [initialId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [bubbles, busy]);

  useEffect(() => {
    return () => {
      const rec = recorderRef.current;
      if (rec && rec.state !== "inactive") {
        rec.onstop = null;
        rec.stop();
      }
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  async function ensureConversation(): Promise<string> {
    if (conversationRef.current) return conversationRef.current;
    const created = await api<Conversation>("/conversations", { method: "POST", json: {} });
    conversationRef.current = created.id;
    router.replace(`/talk?c=${created.id}`, { scroll: false });
    return created.id;
  }

  async function speak(text: string, urgent: boolean) {
    try {
      const audio = await apiBlob("/speech/tts", {
        method: "POST",
        json: { text, crisis: urgent, voice_preference: voice },
      });
      const url = URL.createObjectURL(audio);
      const player = new Audio(url);
      player.onended = () => {
        setSpeaking(false);
        URL.revokeObjectURL(url);
      };
      setSpeaking(true);
      await player.play();
    } catch {
      setSpeaking(false);
      setNotice("Read-aloud is unavailable right now. The reply is shown above.");
    }
  }

  function showTurn(userText: string, turn: ChatTurn) {
    setBubbles((prev) => [
      ...prev,
      { key: `u-${turn.user_message_id}`, role: "user", content: userText },
      { key: `a-${turn.assistant_message_id}`, role: "assistant", content: turn.assistant_content },
    ]);
    if (turn.crisis_contacts?.length) setContacts(turn.crisis_contacts);
    if (turn.requires_human || turn.risk_level === "crisis") setCrisis(true);
    void speak(turn.assistant_content, turn.risk_level === "crisis");
  }

  async function sendVoice(blob: Blob) {
    setBusy(true);
    setError(null);
    try {
      const id = await ensureConversation();
      const form = new FormData();
      form.append("audio", blob, "speech.webm");
      const result = await api<VoiceTurn>(`/conversations/${id}/voice`, { method: "POST", body: form });
      showTurn(result.transcript, result.turn);
    } catch (err) {
      setError(voiceErrorText(err));
    } finally {
      setBusy(false);
    }
  }

  async function startRecording() {
    setError(null);
    setNotice(null);
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Voice is not supported in this browser. Type your message below.");
      return;
    }
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError("Microphone access is blocked. Allow it in your browser settings, or type below.");
      return;
    }
    streamRef.current = stream;
    const mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : undefined;
    const rec = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    chunksRef.current = [];
    rec.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    rec.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunksRef.current, { type: rec.mimeType || "audio/webm" });
      void sendVoice(blob);
    };
    rec.start();
    recorderRef.current = rec;
    setRecording(true);
  }

  function stopRecording() {
    recorderRef.current?.stop();
    setRecording(false);
  }

  async function sendText(e: FormEvent) {
    e.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    setDraft("");
    setBusy(true);
    setError(null);
    try {
      const id = await ensureConversation();
      const turn = await api<ChatTurn>("/conversations/chat", {
        method: "POST",
        json: { conversation_id: id, message: text },
      });
      showTurn(text, turn);
    } catch {
      setError("Could not send your message. Try again.");
      setDraft(text);
    } finally {
      setBusy(false);
    }
  }

  async function changeVoice(preference: VoicePreference) {
    const previous = voice;
    setVoice(preference);
    try {
      const updated = await api<User>("/auth/me/voice", {
        method: "PATCH",
        json: { preference },
      });
      setVoice(updated.voice_preference);
    } catch {
      setVoice(previous);
      setNotice("Could not save your voice preference. Try again.");
    }
  }

  async function sos() {
    setCrisis(true);
    try {
      const result = await api<{ contacts: string[] }>("/escalation/request", {
        method: "POST",
        json: { reason: "SOS pressed on talk screen", urgency: "crisis" },
      });
      setContacts(result.contacts.length ? result.contacts : FALLBACK_CONTACTS);
    } catch {
      setContacts(FALLBACK_CONTACTS);
    }
  }

  const stage = recording
    ? "Listening. Tap to send."
    : busy
      ? "Thinking…"
      : speaking
        ? "Speaking…"
        : "Tap to talk";

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Talk</h1>
          <p className="text-[rgba(238,243,255,0.6)] mt-1">
            Speak or type. Replies are read aloud. Nothing is kept as audio unless you opt in.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="voice-preference" className="text-xs text-[rgba(238,243,255,0.6)]">
            Voice
          </label>
          <select
            id="voice-preference"
            className="input !w-auto !py-1.5 text-sm"
            value={voice}
            onChange={(e) => void changeVoice(e.target.value as VoicePreference)}
          >
            <option value="auto">Auto</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
          </select>
          <button onClick={sos} className="btn bg-[rgb(200,40,40)] text-white px-4 py-2 text-sm">
            SOS
          </button>
        </div>
      </div>

      {crisis && (
        <section className="alert-crisis space-y-2">
          <div className="flex items-start justify-between gap-4">
            <p className="font-semibold">Reach a person now</p>
            <button onClick={() => setCrisis(false)} className="text-sm text-[rgba(238,243,255,0.6)] hover:text-white">
              Dismiss
            </button>
          </div>
          <ul className="text-sm space-y-1 text-[rgba(238,243,255,0.9)]">
            {contacts.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
          <p className="text-xs text-[rgba(238,243,255,0.6)]">If you are in immediate danger, call now.</p>
        </section>
      )}

      <section className="panel flex flex-col items-center gap-4 py-8">
        <button
          onClick={recording ? stopRecording : startRecording}
          disabled={busy}
          aria-label={recording ? "Stop and send" : "Start talking"}
          className={`h-28 w-28 rounded-full flex items-center justify-center text-white text-sm font-semibold transition-all disabled:opacity-50 ${
            recording
              ? "bg-[rgb(200,40,40)] shadow-[0_0_0_12px_rgba(200,40,40,0.2)] animate-pulse"
              : "bg-[rgb(27,79,216)] shadow-[0_10px_40px_rgba(27,79,216,0.5)] hover:brightness-110"
          }`}
        >
          {recording ? "Send" : "Talk"}
        </button>
        <p className="text-sm text-[rgba(238,243,255,0.7)]" aria-live="polite">{stage}</p>
      </section>

      {error && <div className="alert-error">{error}</div>}
      {notice && <div className="alert-error">{notice}</div>}

      <section className="space-y-3">
        {bubbles.length === 0 && (
          <p className="text-sm text-center text-[rgba(238,243,255,0.5)]">
            Start by tapping Talk, or type a message below.
          </p>
        )}
        {bubbles.map((b) => (
          <div key={b.key} className={`flex ${b.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-[0.95rem] leading-relaxed whitespace-pre-wrap ${
                b.role === "user"
                  ? "bg-[rgba(27,79,216,0.3)] border border-[rgba(111,200,255,0.2)]"
                  : "panel !p-4"
              }`}
            >
              {b.content}
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </section>

      <form onSubmit={sendText} className="sticky bottom-4 flex gap-2">
        <input
          className="input"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Or type here…"
          maxLength={10000}
          disabled={busy || recording}
        />
        <button type="submit" disabled={busy || recording || !draft.trim()} className="btn btn-primary px-5 disabled:opacity-50">
          Send
        </button>
      </form>
    </div>
  );
}

function voiceErrorText(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.detail === "no_speech_detected") return "I didn't catch that. Tap Talk and try again.";
    if (err.status === 503 || err.status === 502) {
      return "Voice is not available right now. Type your message below.";
    }
  }
  return "Something went wrong with your voice message. Try again or type below.";
}
