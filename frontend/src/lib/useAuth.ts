"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api, clearTokens, hasToken, type User } from "@/lib/api";

/** Loads the signed-in user. Sends visitors to /login, and students who have not finished onboarding to /onboarding. */
export function useAuth(): { user: User | null; loading: boolean } {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!hasToken()) {
      router.replace("/login");
      return;
    }
    let active = true;
    api<User>("/auth/me")
      .then((me) => {
        if (!active) return;
        setUser(me);
        setLoading(false);
        if (me.role === "student" && !me.onboarded && pathname !== "/onboarding") router.replace("/onboarding");
      })
      .catch(() => {
        if (!active) return;
        clearTokens();
        router.replace("/login");
      });
    return () => {
      active = false;
    };
  }, [router, pathname]);

  return { user, loading };
}

export function destinationFor(user: User): string {
  if (!user.onboarded) return "/onboarding";
  return user.role === "student" ? "/talk" : "/sessions";
}
