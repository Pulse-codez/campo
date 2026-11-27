export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const ACCESS_KEY = "csc_access";
const REFRESH_KEY = "csc_refresh";

export type Role = "student" | "peer_counsellor" | "counsellor" | "admin";
export type ConsentScope = "counselling" | "emergency_contact" | "research" | "analytics";
export type SessionStatus = "requested" | "booked" | "completed" | "cancelled";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: Role;
  university_id: string;
  onboarded: boolean;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface University {
  id: string;
  name: string;
  slug: string;
  domains: string[];
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  risk_level: string | null;
  created_at: string;
}

export interface ChatTurn {
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  assistant_content: string;
  risk_level: string;
  requires_human: boolean;
}

export interface VoiceTurn {
  transcript: string;
  turn: ChatTurn;
}

export interface CounsellingSession {
  id: string;
  student_name: string | null;
  topic: string;
  preferred_time: string | null;
  scheduled_at: string | null;
  status: SessionStatus;
  counsellor_id: string | null;
  created_at: string;
}

export interface ConsentItem {
  scope: ConsentScope;
  granted: boolean;
  policy_version: string;
  updated_at: string;
}

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

export function saveTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function hasToken(): boolean {
  return typeof window !== "undefined" && !!localStorage.getItem(ACCESS_KEY);
}

type ApiInit = Omit<RequestInit, "body"> & { json?: unknown; body?: BodyInit | null };

async function request(path: string, init: ApiInit = {}): Promise<Response> {
  const { json, ...rest } = init;
  const headers = new Headers(init.headers);
  if (json !== undefined) headers.set("Content-Type", "application/json");
  const token = typeof window !== "undefined" ? localStorage.getItem(ACCESS_KEY) : null;
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers,
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });

  if (!res.ok) {
    let detail = res.statusText || "request_failed";
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail ?? data);
    } catch {
      // Non-JSON error body: keep the status text.
    }
    throw new ApiError(res.status, detail);
  }
  return res;
}

export async function api<T>(path: string, init?: ApiInit): Promise<T> {
  const res = await request(path, init);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export async function apiBlob(path: string, init?: ApiInit): Promise<Blob> {
  const res = await request(path, init);
  return res.blob();
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-KE", { dateStyle: "medium", timeStyle: "short" });
}

export function displayName(user: User): string {
  return user.full_name?.trim() || user.email;
}
