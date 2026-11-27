"use client";

import Link from "next/link";
import { useState } from "react";

const links = [
  { href: "#features", label: "What you can do" },
  { href: "#conditions", label: "Topics" },
  { href: "#facts", label: "How it is built" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-[rgba(238,243,255,0.12)] bg-[rgba(1,3,10,0.8)] backdrop-blur-md">
      <div className="container flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2">
          <span className="rounded-md bg-[rgb(27,79,216)] px-2 py-0.5 text-xs font-bold text-white">
            CSC
          </span>
          <span className="font-bold text-xl tracking-tight">Campus Support</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-sm font-medium text-[rgba(238,243,255,0.7)] hover:text-white transition-colors"
            >
              {l.label}
            </Link>
          ))}
          <Link
            href="/login"
            className="text-sm font-medium text-[rgba(238,243,255,0.7)] hover:text-white transition-colors"
          >
            Log in
          </Link>
          <Link href="/register" className="btn btn-primary text-sm px-4 py-2">
            Sign up
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
