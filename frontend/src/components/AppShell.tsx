"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useContext, type ReactNode } from "react";

import ThemeToggle from "@/components/ThemeToggle";
import { clearTokens, type Role, type User } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

const UserContext = createContext<User | null>(null);

export function useUser(): User {
  const user = useContext(UserContext);
  if (!user) throw new Error("useUser must be used inside AppShell");
  return user;
}

const STUDENT_NAV = [
  { href: "/talk", label: "Talk" },
  { href: "/sessions", label: "Counselling" },
  { href: "/onboarding", label: "Privacy" },
];

const STAFF_NAV = [{ href: "/sessions", label: "Queue" }];

// Navigation mirrors backend RBAC. Admin-only screens have no page yet, so
// admins get the staff navigation until those routes are built.
const NAV_BY_ROLE: Record<Role, typeof STUDENT_NAV> = {
  student: STUDENT_NAV,
  peer_counsellor: STAFF_NAV,
  counsellor: STAFF_NAV,
  admin: STAFF_NAV,
};

export default function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-[rgb(var(--fg)/0.6)]">
        Loading…
      </div>
    );
  }

  const nav = NAV_BY_ROLE[user.role] ?? STUDENT_NAV;

  function logout() {
    clearTokens();
    router.replace("/login");
  }

  return (
    <UserContext.Provider value={user}>
      <div className="min-h-screen flex flex-col">
        <header className="sticky top-0 z-40 border-b border-[rgb(var(--fg)/0.12)] bg-[rgb(var(--bg)/0.85)] backdrop-blur-md">
          <div className="container flex items-center gap-6 h-16">
            <Link href={user.role === "student" ? "/talk" : "/sessions"} className="font-bold tracking-tight">
              Campus Support
            </Link>
            <nav className="flex gap-5 overflow-x-auto">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`text-sm whitespace-nowrap transition-colors ${
                    pathname === item.href ? "text-white" : "text-[rgb(var(--fg)/0.6)] hover:text-[rgb(var(--fg))]"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="ml-auto flex items-center gap-4">
              <span className="hidden sm:inline text-xs text-[rgb(var(--fg)/0.5)]">
                {user.role.replace("_", " ")}
              </span>
              <ThemeToggle />
              <button onClick={logout} className="btn btn-outline text-sm px-3 py-1.5">
                Log out
              </button>
            </div>
          </div>
        </header>
        <main className="container flex-grow py-10">{children}</main>
      </div>
    </UserContext.Provider>
  );
}
