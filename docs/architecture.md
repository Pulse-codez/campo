# Architecture

This document describes how rafiki-chat is built. The product requirements are in `Campus_Support_Companion_Architecture.pdf`. This document describes what is actually in the code.

## 1. Components

```
Browser (Next.js PWA, port 3000)
   |  HTTPS + JWT (Authorization: Bearer)
   v
FastAPI backend (port 8000)
   |-- Auth, universities, onboarding, consent, counselling sessions
   |-- Safety pipeline (rule-based classifier)
   |-- LangGraph orchestrator
   |       |-- Claude adapter (Anthropic API)
   |       '-- Crisis protocol (no model call)
   |-- Speech service (ElevenLabs STT and TTS)
   |-- MCP client ---> FastMCP tool server (port 8001)
   '-- PostgreSQL (SQLAlchemy 2, async)

Background jobs (trigger.dev): planned, not running.
```

| Component | Folder | Technology |
|---|---|---|
| Web app | `frontend/` | Next.js 16, React, Tailwind CSS 4, pnpm |
| API | `backend/` | FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, uv |
| Tool server | `mcp_server/` | FastMCP, Pydantic, uv |
| Jobs | `jobs/` | trigger.dev SDK, TypeScript (placeholder) |
| Docs | `docs/` | Markdown |

## 2. Backend layout

```
backend/app/
  main.py            App setup: CORS, routers, startup (create tables, seed universities)
  core/              Config (pydantic-settings), database engine, JWT helpers, therapist catalogue
  models/            SQLAlchemy models: User, University, ConsentRecord, CounsellingSession,
                     Conversation, Message, AuditLog
  schemas/           Pydantic request and response models
  api/               Route modules, one per area, plus deps.py for auth and role checks
  services/          Business logic: auth, consent, counselling, chat turns, speech, audit, seed
  safety/            Rule-based crisis classifier and risk rules
  orchestrator/      LangGraph graph and the fixed crisis protocol message
  llm/               Claude adapter and the base system prompt
backend/migrations/  Alembic (async template). Empty until the first migration is generated.
backend/tests/       End-to-end API tests (SQLite)
```

## 3. Request flow for a chat message

1. The browser sends `POST /conversations/chat` (text) or `POST /conversations/{id}/voice` (audio) with the access token.
2. For audio, the backend sends the file to ElevenLabs speech-to-text. The raw audio is not stored. Only the transcript continues.
3. `run_turn` in `services/chat_service.py` saves the user message with its risk level.
4. The LangGraph graph runs:
   - `safety_check` classifies the latest user message as `none`, `high`, or `crisis`.
   - If the level is `crisis`, the graph returns the fixed crisis protocol message. **The model is not called.**
   - Otherwise `generate` calls Claude with the base system prompt plus the student's virtual therapist persona.
5. The assistant message is saved with its risk level, and the response returns to the browser.
6. For voice, the browser asks `POST /speech/tts` to read the reply aloud. If TTS is unavailable, the text stays on screen.

Transcripts are never sent to the model before the safety check runs, which is a spec requirement (Section 6).

## 4. Safety pipeline

| Level | Trigger | Response |
|---|---|---|
| `crisis` | Keywords such as "suicide", "kill myself", "self harm", "overdose" | Fixed protocol message, no model call, `requires_human = true` |
| `high` | Keywords such as "hopeless", "worthless", "panic attack" | Model call with the safety system prompt, `requires_human = true` |
| `none` | Everything else | Model call |

Limitations, stated plainly:
- Matching is keyword based. It is English only. The spec requires English, Kiswahili, and Sheng phrase lists plus a classifier, so this is a first step.
- The `escalation` chain (on-call page, 5-minute wait, secondary counsellor, duty officer) is not implemented. It needs trigger.dev. See [status-and-known-issues.md](status-and-known-issues.md).

## 5. Authentication and authorization

- Passwords are hashed with bcrypt (`bcrypt` library, 72-byte limit enforced).
- Access tokens are JWTs valid for 15 minutes. Refresh tokens are valid for 14 days. Both are signed with `JWT_SECRET`.
- Tokens are stored in the browser's `localStorage`. This is simple but weaker than httpOnly cookies. See the known issues list.
- Roles: `student`, `peer_counsellor`, `counsellor`, `admin`. Staff routes use `require_roles` in `api/deps.py`.
- Every user belongs to one university. Staff only see records from their own university.
- Counsellors only see students who have consented to the `counselling` scope. Consent is checked when the list is built, so revoking consent removes the request from the queue immediately.

## 6. Data model

| Table | Purpose | Notes |
|---|---|---|
| `universities` | Tenants for the auth layer | Seeded on startup. `email_domains` is comma separated. `other` accepts unlisted universities. |
| `users` | Accounts | Has `role`, `university_id`, `onboarded`, `concerns`, `therapist_key`, emergency contact, and `university_other_name`. |
| `consent_records` | Append-only consent history | One row per change, with `policy_version`. The latest row per scope is the current choice. |
| `counselling_sessions` | Student requests and bookings | Statuses: `requested`, `booked`, `completed`, `cancelled`. |
| `conversations` | Chat threads | One user each. |
| `messages` | Chat messages | Stores `risk_level` for each message. Bodies are not yet encrypted (see known issues). |
| `monthly_reflections` | Monthly check-ins | One row per user and month (`period` as `YYYY-MM`). Unique on user and period. |
| `kind_notes` | Notes a student writes to someone else | Private to the writer. Recipient name is optional. |
| `audit_logs` | Record of sensitive actions | Written for logins, onboarding, consent changes, counselling status changes, and role changes. Reads are not audited yet. |

Tables are created with `Base.metadata.create_all` at startup for development. Alembic is set up for production migrations, but no migration file has been generated yet. See [getting-started.md](getting-started.md).

## 7. Virtual therapists

Onboarding asks the student to choose concerns: family issues, stress, peer pressure, suicide, or other. The backend recommends one virtual therapist by priority: suicide first, then family issues, peer pressure, stress, and other.

Each therapist is a persona added to the model's system prompt. They are AI companions and are labelled that way. The students can choose any of the five therapists, and the choice is stored on the user. See `backend/app/core/therapists.py`.

These personas have not been clinically reviewed. The spec requires clinical sign-off for crisis-related content.

## 8. Frontend structure

```
frontend/src/
  app/               Routes: /, /login, /help, /onboarding, /talk, /sessions
  components/        Shared UI: AppShell, ThemeToggle, StatusPill, SystemFacts,
                     FeatureCards, ConditionCards, Footer, auth/ (split layout, styles)
  components/originkit/  Hero 49 section, generated by the Originkit CLI and customised
  lib/               api.ts (fetch wrapper and types), useAuth.ts (session and redirects)
```

Theme colours come from CSS variables set on `<html data-theme="light|dark">`. See [frontend.md](frontend.md).

## 9. MCP tool server

A separate FastMCP service exposes five tools: `search_policies`, `find_resources`, `plan_study`, `evaluate_decision`, and `request_escalation`. The backend calls them over MCP with `fastmcp.Client`. The data behind them is placeholder data. See [mcp-server.md](mcp-server.md).

## 10. Decisions and why

| Decision | Reason |
|---|---|
| Claude behind one adapter (`llm/adapter.py`) | Spec Section 5: the conversation model must be swappable. Only the adapter imports the vendor SDK. |
| Crisis path skips the model | Spec Section 1 and 7: a student in danger always reaches a human, whatever the model does. |
| Safety check before the model | Spec Section 6: transcripts go through the safety pipeline first. |
| Single process, async SQLAlchemy | Simple to run locally. Scales later. |
| Tables created at startup | Fast local setup. Alembic takes over once migrations are generated. |
