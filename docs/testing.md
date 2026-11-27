# Testing

## 1. Backend tests

The backend has an end-to-end API suite in `backend/tests/test_api_smoke.py`. It starts the real app, creates the tables, and seeds the universities. It uses a separate SQLite database at `/tmp/opencode/campus_smoke.db`, so PostgreSQL is not needed.

```bash
cd backend
uv run pytest
```

Expected result: 13 passed.

Quieter output (useful because SQL logging is noisy):

```bash
DEBUG=false uv run pytest -q -p no:logging
```

### What the tests cover

| Test | Checks |
|---|---|
| `test_universities_are_seeded` | The seed list includes the expected universities |
| `test_listed_universities_are_available` | All listed universities and `other` are present |
| `test_registration_requires_university_email` | A Gmail address is refused for a listed university |
| `test_other_university_requires_name_and_academic_email` | The `other` path needs a name and a `.ac.ke` or `.edu` email |
| `test_student_onboarding_and_counselling_request` | Counselling is refused without consent, and allowed after onboarding with consent |
| `test_crisis_message_gets_protocol_without_model` | A crisis message returns the protocol with `risk_level` crisis and does not call the model |
| `test_staff_queue_is_limited_to_own_university_and_consent` | Staff only see their own university's consented students, and cannot act on other universities' requests |
| `test_students_cannot_open_the_staff_queue_actions` | Students get 403 on staff actions |
| `test_revoked_consent_hides_request_from_staff` | Revoking consent removes the request from the staff queue |
| `test_concerns_list_is_public_to_authenticated_users` | The concerns list is returned to signed-in users |
| `test_recommendation_prioritises_safety` | Suicide outranks other concerns in the recommendation |
| `test_onboarding_stores_recommended_therapist` | Onboarding saves the recommended therapist and concerns |
| `test_onboarding_requires_a_concern` | Onboarding without a concern is refused |

### What is not covered yet

- Chat turns that reach the model. These need a live Anthropic key, so the suite avoids non-crisis messages.
- Voice (speech-to-text and text-to-speech). These need ElevenLabs keys.
- The MCP-backed routes. These need the MCP server running.
- Alembic migrations. None have been generated yet.
- Authentication on the unprotected routes (see known issues). The suite does not test them yet.

## 2. Linting

```bash
cd backend && uv run ruff check .
cd mcp_server && uv run ruff check .
cd frontend && pnpm lint
```

All three currently pass.

## 3. Frontend build

```bash
cd frontend && pnpm build
```

The build type-checks the app and prerenders static pages. It does not run the browser tests.

## 4. Visual checks

Screenshots were taken with the bundled Chromium from Playwright's cache:

```bash
CHROME=~/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome
"$CHROME" --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --window-size=1400,900 --virtual-time-budget=8000 \
  --screenshot=/tmp/opencode/login.png "http://localhost:3100/login?theme=light"
```

Use `?theme=light` or `?theme=dark` to choose the theme. The frontend must be running (`pnpm start -p 3100` after a build).

Screens that have been checked this way: login (dark and light), sign-up (dark and light), and the landing page (light). Authenticated pages (`/talk`, `/sessions`, `/onboarding`) have not been checked by screenshot because they need a signed-in session.

## 5. Manual testing checklist

Do these before a pilot:

- [ ] Sign up with a valid university email, and with a wrong one (should be refused).
- [ ] Sign up with **Other** and a `.ac.ke` email, then with a Gmail address (should be refused).
- [ ] Sign in, complete onboarding, and confirm you land on `/talk`.
- [ ] Choose suicide as a concern and confirm the crisis panel appears.
- [ ] Send a crisis message in chat and confirm the protocol reply and no model call.
- [ ] Record a voice message (needs ElevenLabs keys) and confirm transcript and playback.
- [ ] Request counselling, then revoke consent, and confirm the request disappears from the staff queue.
- [ ] Toggle light and dark mode on every page and check text is readable.
- [ ] Test on a low-end Android phone in the installed PWA.
