# Backend API reference

Base URL in development: `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

## Conventions

- Request and response bodies are JSON unless noted.
- Authenticated routes need `Authorization: Bearer <access_token>`.
- Errors use `{"detail": "<code>"}`. Codes are short strings such as `invalid_credentials`, so the frontend can show the right message.
- Dates are ISO 8601 with timezone.
- IDs are UUIDs.

## Auth levels

| Level | Meaning |
|---|---|
| Public | No token needed |
| Student | Any signed-in user |
| Staff | `peer_counsellor`, `counsellor`, or `admin` |
| Admin | `admin` only |

## Health

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/` | Public | Service name and version |
| GET | `/health` | Public | Health check |

## Universities and auth

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/universities` | Public | List active universities. Includes `other`. |
| POST | `/auth/register` | Public | Create a student account. Body: `email`, `password` (8 to 72 characters), `full_name`, `university_id`, `other_university_name` (required for `other`). Returns tokens, but the frontend does not keep them. |
| POST | `/auth/login` | Public | Body: `email`, `password`. Returns `access_token`, `refresh_token`. |
| POST | `/auth/refresh` | Refresh token as bearer | Returns a new token pair. |
| GET | `/auth/me` | Student | The signed-in user, including `role`, `onboarded`, `concerns`, `therapist_key`. |

By default any email address can register (`ENFORCE_UNIVERSITY_EMAIL=false`). With the setting on, the domain rules below apply.

Registration errors:

| `detail` | Meaning |
|---|---|
| `university_not_found` | Unknown or inactive university |
| `email_domain_not_allowed` | Email is not on the chosen university's domain (only when `ENFORCE_UNIVERSITY_EMAIL=true`) |
| `other_university_name_required` | `other` chosen without a name |
| `other_email_not_accepted` | Unlisted university with an email that does not end in `.ac.ke` or `.edu` |
| `email_already_registered` | Email already exists (HTTP 409) |

## Onboarding, consent, and concerns

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/concerns` | Student | List of concern keys and labels |
| GET | `/therapists` | Student | List of virtual therapists |
| POST | `/therapists/recommend` | Student | Body: `concerns`. Returns `primary`, `alternatives`, `show_crisis_resources`. |
| POST | `/onboarding` | Student | Completes onboarding. Body: `concerns` (at least one), `therapist_key` (optional), `consents` (map of scope to boolean), `emergency_contact_name` and `emergency_contact_phone` (required if `emergency_contact` is true), `policy_version`. Returns the user. |
| POST | `/consents` | Student | Records a consent change. Body: `scope`, `granted`, `policy_version`. Returns the new record. |
| GET | `/consents/me` | Student | Current value for each consent scope |

Consent scopes: `counselling`, `emergency_contact`, `research`, `analytics`.

## Conversations and voice

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/conversations` | Student | Create an empty conversation |
| GET | `/conversations` | Student | The user's conversations, newest first |
| GET | `/conversations/{id}/messages` | Student | Messages in a conversation, oldest first |
| POST | `/conversations/chat` | Student | Body: `message`, `conversation_id` (optional). Runs one safety-checked turn. Returns `assistant_content`, `risk_level`, `requires_human`, and IDs. |
| POST | `/conversations/{id}/voice` | Student | Multipart upload with field `audio`. Transcribes, then runs the same turn as text. Returns `transcript` and `turn`. |

Voice errors: `no_speech_detected` (422), `empty_audio` (422), `elevenlabs_not_configured` (503), `speech_provider_error` (502).

## Speech

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/speech/tts` | Student | Body: `text` (max 2000 characters), `crisis` (optional, selects the crisis voice). Returns `audio/mpeg`. |

## Counselling sessions

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/counselling-sessions` | Student or staff | Students: their own requests. Staff: requests from their university where the student has consented to counselling and the session is unassigned or assigned to them. |
| POST | `/counselling-sessions` | Student | Body: `topic`, `preferred_time` (optional). Requires counselling consent (`counselling_consent_required`, 403). |
| PATCH | `/counselling-sessions/{id}` | Staff | Body: `status` (`requested`, `booked`, `completed`, `cancelled`), `scheduled_at` (optional). Accepting a request (`booked`) assigns it to the caller. Returns 404 for other universities or other counsellors' sessions. |

## Admin

| Method | Path | Auth | Purpose |
|---|---|---|---|
| PATCH | `/admin/users/{user_id}/role` | Admin | Body: `role`. Only for users in the admin's own university. There is no admin screen; use this endpoint directly. |

## Monthly check-in

Students write once a month about how they are feeling and where they are going in life.

Writing opens in the last 7 days of each month. Students can also write for any of the last three months they missed. One check-in per month.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/checkin/status` | Student | `current_period`, `open_periods` (months you can write for now), `submitted_periods` |
| GET | `/checkin` | Student | Your past check-ins, newest first |
| POST | `/checkin` | Student | Body: `feelings`, `direction`, `period` (optional, `YYYY-MM`, defaults to this month). Returns `entry`, `requires_human`, `contacts`. Crisis words still save the entry, and set `requires_human`. |

Errors: `already_submitted` (409), `period_in_future`, `period_too_old`, `opens_in_last_week_of_month` (422).

## Kind words

Two features: a short message written by Claude, and kind notes a student writes to someone.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/kindness/message` | Student | Body: `theme` (`encouragement`, `hope`, `rest`, `self_kindness`). Returns `message`. The prompt is fixed on the server. Returns 503 `ai_not_configured` when no Anthropic key is set. |
| GET | `/kindness/notes` | Student | Your saved notes, newest first |
| POST | `/kindness/notes` | Student | Body: `body` (required, up to 2000 characters), `recipient` (optional) |
| DELETE | `/kindness/notes/{id}` | Student | Delete one of your notes (404 for anyone else's) |

## Safety, resources, and tools

These routes forward work to the MCP server or run the classifier. **They do not require a token yet.** See [status-and-known-issues.md](status-and-known-issues.md).

| Method | Path | Purpose |
|---|---|---|
| POST | `/safety/check` | Body: `text`. Returns `level`, `requires_human`, `reasons`, `crisis_contacts`. |
| POST | `/resources/find` | Body: `resource_type`, `location`, `hours`. Calls the MCP `find_resources` tool. |
| POST | `/escalation/request` | Body: `reason`, `urgency` (`routine`, `urgent`, `crisis`), `preferred_channel`. Calls `request_escalation`. |
| POST | `/study/plan` | Body: `units`, `hours_per_week`, `energy_level`, `exam_weeks_away`. Calls `plan_study`. |
| POST | `/decision/evaluate` | Body: `situation`, `options`, `values`. Calls `evaluate_decision`. |
| GET | `/policies/search` | Query: `q`, `category`, `limit`. Calls `search_policies`. |

If the MCP server is not running, these return `502` with `mcp_unavailable`.

## Quick examples

```bash
# List universities
curl http://localhost:8000/universities

# Register a student (use a real university email for your campus)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@uonbi.ac.ke","password":"longpassword1","full_name":"Test","university_id":"<id from /universities>"}'

# Log in and keep the access token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@uonbi.ac.ke","password":"longpassword1"}'

# Send a chat message
curl -X POST http://localhost:8000/conversations/chat \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"Exams are stressing me out"}'
```
