"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { api, clearTokens, hasToken, type Role, type User } from "@/lib/api";

const UserContext = createContext<User | null>(null);

export function useUser(): User {
  const user = useContext(UserContext);
  if (!user) throw new Error("useUser must be used inside AppShell");
  return user;
}

const STUDENT_NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/talk", label: "Talk" },
  { href: "/sessions", label: "Sessions" },
  { href: "/onboarding", label: "Consent" },
];

const STAFF_NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/sessions", label: "Queue" },
];

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
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (!hasToken()) {
      router.replace("/login");
      return;
    }
    api<User>("/auth/me")
      .then((me) => {
        setUser(me);
        if (!me.onboarded && pathname !== "/onboarding") router.replace("/onboarding");
      })
      .catch(() => {
        clearTokens();
        router.replace("/login");
      });
  }, [router, pathname]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-[rgba(238,243,255,0.6)]">
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
        <header className="sticky top-0 z-40 border-b border-[rgba(238,243,255,0.12)] bg-[rgba(1,3,10,0.85)] backdrop-blur-md">
          <div className="container flex items-center gap-6 h-16">
            <Link href="/dashboard" className="font-bold tracking-tight">
              Campus Support
            </Link>
            <nav className="flex gap-5 overflow-x-auto">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`text-sm whitespace-nowrap transition-colors ${
                    pathname === item.href ? "text-white" : "text-[rgba(238,243,255,0.6)] hover:text-white"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="ml-auto flex items-center gap-4">
              <span className="hidden sm:inline text-xs text-[rgba(238,243,255,0.5)]">
                {user.role.replace("_", " ")}
              </span>
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
