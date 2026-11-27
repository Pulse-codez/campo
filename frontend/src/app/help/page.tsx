import Link from "next/link";

import { BrandMark } from "@/components/auth/SplitLayout";
import ThemeToggle from "@/components/ThemeToggle";

const CONTACTS = [
  { name: "National mental health helpline", detail: "1199 · 24/7 · free" },
  { name: "Campus security", detail: "+254 700 000 999 · 24/7 · on campus" },
  { name: "Nearest hospital emergency department", detail: "Go now, or ask someone to take you" },
];

export default function HelpPage() {
  return (
    <main className="min-h-screen bg-[rgb(var(--surface))] px-6 py-12 text-[rgb(var(--fg))]">
      <div className="mx-auto max-w-lg space-y-8">
        <div className="flex items-center justify-between">
          <BrandMark />
          <ThemeToggle />
        </div>
        <div>
          <p className="text-[11px] font-semibold tracking-[0.2em] text-[rgb(var(--fg)/0.62)]">URGENT HELP</p>
          <h1 className="mt-3 text-4xl font-bold">Reach a person now.</h1>
          <p className="mt-3 text-[rgb(var(--fg)/0.62)]">
            If you are in immediate danger, call or go to one of these. You do not need an account.
          </p>
        </div>

        <ul className="space-y-3">
          {CONTACTS.map((c) => (
            <li key={c.name} className="rounded-xl border border-[rgb(var(--danger)/0.4)] bg-[rgb(var(--danger)/0.1)] p-4">
              <p className="font-semibold text-[rgb(var(--danger))]">{c.name}</p>
              <p className="text-sm text-[rgb(var(--danger))]">{c.detail}</p>
            </li>
          ))}
        </ul>

        <p className="text-sm text-[rgb(var(--fg)/0.62)]">
          This service is not an emergency service. Verify local numbers with your campus before relying on them.
        </p>

        <Link href="/login" className="block rounded-lg border border-[rgb(var(--fg)/0.15)] py-3 text-center text-sm font-semibold text-[rgb(var(--fg))] hover:bg-[rgb(var(--fg)/0.05)]">
          Back to sign in
        </Link>
      </div>
    </main>
  );
}
