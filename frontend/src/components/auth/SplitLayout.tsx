import Link from "next/link";
import type { ReactNode } from "react";

import ThemeToggle from "@/components/ThemeToggle";

export function BrandMark() {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span className="relative inline-block h-5 w-5">
        <span className="absolute inset-0 rotate-45 rounded-[3px] border-2 border-[rgb(var(--accent))]" />
      </span>
      <span>
        <span className="block text-lg font-bold leading-none text-[rgb(var(--fg))]">rafiki-chat</span>
        <span className="block text-[10px] tracking-[0.25em] text-[rgb(var(--fg)/0.62)]">STUDENT SUPPORT</span>
      </span>
    </Link>
  );
}

export function Emblem() {
  return (
    <svg viewBox="0 0 280 220" className="h-56 w-72" aria-hidden="true">
      <defs>
        <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#6E8FE6" />
          <stop offset="100%" stopColor="#1B4FD8" />
        </linearGradient>
      </defs>
      <ellipse
        cx="120"
        cy="120"
        rx="110"
        ry="46"
        transform="rotate(-18 120 120)"
        fill="none"
        strokeWidth="1"
        strokeDasharray="3 4"
        style={{ stroke: "rgb(var(--link)/0.5)" }}
      />
      <rect x="70" y="60" width="110" height="110" rx="18" transform="rotate(18 125 115)" fill="url(#tile)" opacity="0.7" />
      <rect x="62" y="70" width="110" height="110" rx="18" transform="rotate(-6 117 125)" fill="url(#tile)" opacity="0.9" />
      <path d="M118 96 L123 111 L138 116 L123 121 L118 136 L113 121 L98 116 L113 111 Z" fill="#FFFFFF" />
      <rect x="196" y="58" width="48" height="44" rx="10" style={{ fill: "rgb(var(--surface))", stroke: "rgb(var(--fg)/0.15)" }} />
      <text x="220" y="87" textAnchor="middle" fontFamily="Georgia, serif" fontStyle="italic" fontSize="20" style={{ fill: "rgb(var(--accent))" }}>
        A+
      </text>
    </svg>
  );
}

export default function SplitLayout({ left, children }: { left: ReactNode; children: ReactNode }) {
  return (
    <div className="grid min-h-screen bg-[rgb(var(--surface))] text-[rgb(var(--fg))] lg:grid-cols-2">
      <aside className="hidden flex-col bg-[rgb(var(--accent)/0.1)] px-12 py-10 text-[rgb(var(--fg))] lg:flex">{left}</aside>
      <section className="relative flex flex-col items-center justify-center px-6 py-12">
        <div className="absolute right-4 top-4">
          <ThemeToggle />
        </div>
        <div className="w-full max-w-sm lg:hidden mb-8">
          <BrandMark />
        </div>
        {children}
      </section>
    </div>
  );
}
