# Status and known issues

This page is the honest picture: what works, what is placeholder, and what must change before real students use the system.

## 1. What works

| Area | Status |
|---|---|
| Sign up with a university email (listed universities and `other`) | Working |
| Sign in and token refresh | Working |
| Onboarding: concerns, virtual therapist, privacy choices | Working |
| Consent records (append-only, revocable) | Working |
| Chat with the safety check before the model | Working (keyword-based classifier) |
| Crisis protocol with no model call | Working |
| Voice input and playback | Written, needs ElevenLabs keys to test |
| Counselling requests and staff queue, scoped by university and consent | Working |
| Staff role assignment through the admin endpoint | Working (no admin screen) |
| Light and dark themes on every page | Working |
| Automated backend tests (13) | Passing |

## 2. Placeholder or partial

| Area | What is missing |
|---|---|
| Safety classifier | Keyword lists only, English only. The spec requires Kiswahili and Sheng lists and a trained classifier. Needs clinical sign-off. |
| Escalation chain | Not built. The spec's chain (on-call page, 5-minute wait, secondary counsellor, duty officer) needs trigger.dev. The `jobs/` folder is an empty placeholder. |
| Virtual therapists | Five personas, not clinically reviewed. They are AI companions, not clinicians. |
| University email domains | Best guesses for UON, KCA, TUK, Zetech, Daystar, Riara, and the others. Each must be checked with the institution. |
| `other` university accounts | Accepted with a `.ac.ke` or `.edu` email, but no admin review step exists to verify them. |
| Resources, policies, study planner, decision lab, escalation tool | Static data inside the MCP server. Not connected to real systems. |
| Speech-to-speech | Turn based: record, transcribe, reply, read aloud. The spec's real-time agent mode is not built. |
| Pre-generated crisis audio | Not built. Crisis replies are synthesised live. |
| Vendor model IDs | `scribe_v1` and `eleven_multilingual_v2` should be checked against ElevenLabs' current names. |
| Footer pages (`/privacy`, `/terms`, `/accessibility`) | Linked but not built. |
| Password reset | Not built. |
| Email or OTP verification | Not built. Accounts are created by the email owner with no confirmation step. |
| Landing hero video | The hero uses a WebGL effect. Its image and CDN assets should move to `public/` before production (Originkit guidance). |

## 3. Known issues (fix before pilot)

### Security

1. **Several routes have no authentication.** These accept requests from anyone who can reach the server: `POST /safety/check`, `POST /resources/find`, `POST /escalation/request`, `POST /study/plan`, `POST /decision/evaluate`, `GET /policies/search`. The escalation route in particular could be used to create tickets without a login. Fix: add `CurrentUser` to each route in `backend/app/api/`.
2. **Tokens are stored in `localStorage`.** A script injected into the page could read them. The spec asks for short-lived JWTs with refresh rotation. Consider httpOnly cookies.
3. **Refresh tokens are not rotated or revoked.** Logging out does not invalidate them. The refresh endpoint issues a new pair but does not retire the old one.
4. **No rate limiting on login or registration.** Redis is configured but not used.
5. **Message bodies are stored as plain text.** The spec requires field-level encryption. `FIELD_ENCRYPTION_KEY` exists but is not used.
6. **Audit reads are not logged.** The spec requires an audit event for every read of a student record. Only writes and sign-ins are logged.
7. **CORS regex allows any private-network address.** Fine for development. Narrow it or remove it for production.
8. **`JWT_SECRET` in `backend/.env` is a development value.** Replace it before any shared use.

### Data and clinical

9. **Crisis detection is keyword matching.** It will miss messages and flag some harmless ones. It is a backstop, not a clinical tool.
10. **Counsellors are not notified** when a crisis is detected. The protocol message is shown to the student only.
11. **The escalation tool is callable from the open route in item 1.** The spec says the model must not be able to call it. The model cannot call it today because no tool-calling is wired in, but the open route should be closed anyway.

### Engineering

12. **No Alembic migrations exist.** Tables are created at startup. Before production, generate and commit the first migration (`uv run alembic revision --autogenerate -m "initial"` with PostgreSQL running).
13. **Existing databases will not gain new columns.** `create_all` only creates missing tables. If your local database was created before the `concerns`, `therapist_key`, or `university_other_name` columns were added, drop and recreate it, or add the columns with a migration.
14. **Chat history is loaded with a limit of 50 messages** and no paging. Long conversations lose older context.
15. **The MCP server is started by hand.** There is no process manager or health check.

## 4. Decisions needed from the project team

These are not engineering tasks. The spec requires them before build:

- Clinical sign-off for the risk taxonomy, escalation matrix, screening instruments, and crisis templates (Phase 0).
- Written confirmation from Anthropic and ElevenLabs on data residency, retention, training use, deletion, and a data processing agreement under the Kenya Data Protection Act 2019.
- Verification of every university email domain and every helpline number.
- Whether the Digital Health Act 2023 or Commission for University Education rules apply to the pilot campus.
- Which Claude model to use in production.
- Whether the whole app should be light, dark, or both (currently both, with dark as default).

## 5. Build plan position (spec Section 13)

| Phase | Status |
|---|---|
| 0. Clinical and legal foundations | Not started (needs people outside engineering) |
| 1. Safety core | Partial: keyword classifier and crisis protocol. Escalation chain and labelled test set missing. |
| 2. Foundations | Mostly done: API, auth, PWA shell, encrypted store (not yet encrypted), FHIR facade (not built) |
| 3. Conversation | Partial: Claude adapter, LangGraph orchestrator, MCP tools (placeholder data). Adapter contract tests missing. |
| 4. Voice | Written. Latency not measured. Pre-generated crisis audio missing. |
| 5. Student tools | Partial: study planner and decision lab exist as MCP tools, no usability testing |
| 6. Clinical integration | Not started: questionnaires (C-SSRS, PHQ-9, GAD-7), flags, ServiceRequest, FHIR facade |
| 7. Pilot | Not started |
