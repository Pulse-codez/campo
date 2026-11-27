"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell, { useUser } from "@/components/AppShell";
import StatusPill from "@/components/StatusPill";
import {
  api,
  displayName,
  formatDateTime,
  type ConsentItem,
  type CounsellingSession,
  type Conversation,
} from "@/lib/api";

export default function DashboardPage() {
  return (
    <AppShell>
      <DashboardContent />
    </AppShell>
  );
}

function DashboardContent() {
  const user = useUser();
  const isStudent = user.role === "student";
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sessions, setSessions] = useState<CounsellingSession[]>([]);
  const [consents, setConsents] = useState<ConsentItem[]>([]);

  useEffect(() => {
    if (isStudent) {
      api<Conversation[]>("/conversations").then((c) => setConversations(c.slice(0, 5)));
      api<ConsentItem[]>("/consents/me").then(setConsents);
    }
    api<CounsellingSession[]>("/counselling-sessions").then(setSessions);
  }, [isStudent]);

  const counsellingOn = consents.some((c) => c.scope === "counselling" && c.granted);
  const openRequests = sessions.filter((s) => s.status === "requested").length;
  const booked = sessions.filter((s) => s.status === "booked").length;

  return (
    <div className="space-y-10">
      <div>
        <p className="text-sm text-[rgba(238,243,255,0.5)]">Welcome back</p>
        <h1 className="text-3xl font-bold">{displayName(user)}</h1>
      </div>

      {isStudent ? (
        <>
          <section className="grid md:grid-cols-3 gap-4">
            <ActionCard href="/talk" title="Talk to the companion" detail="Speak or type. Tap the mic to start." />
            <ActionCard
              href="/sessions"
              title="Request counselling"
              detail={counsellingOn ? "Book time with a campus counsellor." : "Turn on counselling consent first."}
            />
            <ActionCard href="/onboarding" title="Privacy choices" detail="See and change what is shared." />
          </section>

          <div className="grid md:grid-cols-2 gap-6">
            <section className="panel space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">Recent conversations</h2>
                <Link href="/talk" className="text-sm text-[#6FC8FF] hover:underline">New</Link>
              </div>
              {conversations.length === 0 ? (
                <p className="text-sm text-[rgba(238,243,255,0.55)]">No conversations yet.</p>
              ) : (
                <ul className="divide-y divide-[rgba(238,243,255,0.08)]">
                  {conversations.map((c) => (
                    <li key={c.id} className="py-3">
                      <Link href={`/talk?c=${c.id}`} className="flex justify-between gap-4 hover:text-[#6FC8FF]">
                        <span>Conversation</span>
                        <span className="text-sm text-[rgba(238,243,255,0.5)]">{formatDateTime(c.updated_at)}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="panel space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">Counselling requests</h2>
                <Link href="/sessions" className="text-sm text-[#6FC8FF] hover:underline">View all</Link>
              </div>
              {sessions.length === 0 ? (
                <p className="text-sm text-[rgba(238,243,255,0.55)]">
                  No requests yet. Your counsellor sees a request only if you have turned on counselling consent.
                </p>
              ) : (
                <ul className="divide-y divide-[rgba(238,243,255,0.08)]">
                  {sessions.slice(0, 4).map((s) => (
                    <li key={s.id} className="py-3 flex justify-between gap-4">
                      <span>{s.topic}</span>
                      <StatusPill status={s.status} />
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>

          <section className="alert-crisis">
            <p className="font-semibold">In immediate danger?</p>
            <p className="text-sm mt-1 text-[rgba(238,243,255,0.85)]">
              Call <strong>1199</strong> (national mental health helpline, 24/7, free) or go to the nearest hospital
              emergency department. On campus, contact security on +254 700 000 999.
            </p>
          </section>
        </>
      ) : (
        <>
          <section className="grid md:grid-cols-3 gap-4">
            <Stat label="New requests" value={openRequests} />
            <Stat label="Booked" value={booked} />
            <ActionCard href="/sessions" title="Open the queue" detail="Accept, schedule and close sessions." />
          </section>
          <p className="text-sm text-[rgba(238,243,255,0.6)]">
            You see only students at your university who have consented to counselling.
          </p>
        </>
      )}
    </div>
  );
}

function ActionCard({ href, title, detail }: { href: string; title: string; detail: string }) {
  return (
    <Link href={href} className="card group">
      <h3 className="font-semibold text-lg group-hover:text-[#6FC8FF] transition-colors">{title}</h3>
      <p className="text-sm text-[rgba(238,243,255,0.6)] mt-1">{detail}</p>
    </Link>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="panel">
      <p className="text-sm text-[rgba(238,243,255,0.6)]">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}

