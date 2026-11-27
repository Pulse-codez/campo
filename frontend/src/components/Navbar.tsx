"use client";

import Link from "next/link";
import { useState } from "react";

const links = [
  { href: "/", label: "Home" },
  { href: "/resources", label: "Resources" },
  { href: "/find-support", label: "Find Support" },
  { href: "/study-planner", label: "Study Planner" },
  { href: "/about", label: "About" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-white/60 bg-white/80 backdrop-blur-md">
      <div className="container flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2">
          <span className="rounded-md bg-[rgb(20,137,103)] px-2 py-0.5 text-xs font-bold text-white">
            CSC
          </span>
          <span className="font-bold text-xl tracking-tight">Campus Support</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-sm font-medium text-[rgb(107,114,128)] hover:text-[rgb(20,137,103)] transition-colors"
            >
              {l.label}
            </Link>
          ))}
          <Link
            href="/login"
            className="btn btn-primary text-sm px-4 py-2"
          >
            Log in
          </Link>
        </nav>

        <button
          className="md:hidden btn-ghost"
          onClick={() => setOpen(!open)}
          aria-label="Open menu"
        >
          ☰
        </button>
      </div>
    </header>
  );
}
