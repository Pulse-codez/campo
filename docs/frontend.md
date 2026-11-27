# Frontend

The web app is a Next.js 16 application (App Router, React, TypeScript, Tailwind CSS 4). It is designed as a PWA: it has a web manifest and a service worker.

## 1. Pages

| Route | Who sees it | Purpose |
|---|---|---|
| `/` | Everyone | Landing page: hero, what you can do, topics, "How it is built" facts |
| `/login` | Everyone | Sign in tab and New student tab (sign-up). Accepts `?tab=new`. |
| `/help` | Everyone | Urgent help contacts, no account needed |
| `/onboarding` | Signed-in students | Three steps: concerns, virtual therapist, privacy choices |
| `/talk` | Signed-in students | Chat with text and voice (speech to speech, turn by turn) |
| `/sessions` | Students and staff | Students: request counselling. Staff: the session queue. |

The `/dashboard` page was removed on purpose. Students land on `/talk` after sign-in.

Links to `/privacy`, `/terms`, and `/accessibility` in the footer point to pages that do not exist yet.

## 2. User flows

### Sign up and sign in
1. Choose **Sign up** (goes to `/login?tab=new`).
2. Pick a university from the list. If it is not listed, pick **Other (not listed)** and type the name. Use an email ending in `.ac.ke` or `.edu` for unlisted universities.
3. Submit. The page switches to **Sign in** with a success message and your email filled in. Sign-up does not log you in.
4. Sign in. The app asks `/auth/me` where to go:
   - Not onboarded: `/onboarding`
   - Student: `/talk`
   - Staff: `/sessions`

### Onboarding
1. **What's on your mind?** Choose one or more of: family issues, stress, peer pressure, suicide, other. Choosing suicide shows crisis contacts straight away. You can continue.
2. **Choose your virtual therapist.** The recommended therapist is labelled. You may pick any of the five.
3. **Your privacy, your choice.** Consent toggles, emergency contact (only if that consent is on), and a required acknowledgement. Finish takes you to `/talk`.

Returning users who open `/onboarding` again see their saved choices and can change them.

### Chat and voice (`/talk`)
- **Talk** button: starts recording with the browser microphone. Press it again to send.
- The reply appears as text and is read aloud when ElevenLabs is configured.
- **Typing** works as a fallback under the voice button.
- **SOS** button: shows crisis contacts and records a crisis escalation request.
- If a reply is flagged as needing a human, a red panel with contacts appears at the top.

### Counselling (`/sessions`)
- Students need counselling consent to send a request. If consent is off, the page explains how to turn it on.
- Staff see only requests from their university, where the student has consented. They can accept (**Accept**), complete, or cancel a request.

## 3. Theme (light and dark)

- Dark is the default. The choice is saved in `localStorage` under `csc_theme`.
- The toggle appears in the page header or top-right corner of the page.
- The theme is applied by a small script in `src/app/layout.tsx`, before the first paint, so the page does not flash.
- `?theme=light` or `?theme=dark` in the URL overrides the saved choice, which is useful for screenshots and links.
- The accent colour is blue (`#1B4FD8`) in both themes.

Colours are CSS variables defined in `src/app/globals.css`:

| Variable | Dark | Light | Use |
|---|---|---|---|
| `--bg` | `1 3 10` | `244 247 252` | Page background |
| `--surface` | `12 16 30` | `255 255 255` | Cards and panels |
| `--fg` | `238 243 255` | `15 23 42` | Text |
| `--link` | `111 200 255` | `27 79 216` | Links, highlights |
| `--accent` | `27 79 216` | `27 79 216` | Buttons |
| `--accent-hover` | `40 95 240` | `21 64 180` | Button hover |
| `--danger` | `255 120 120` | `185 28 28` | Crisis and error text |

Use them in Tailwind like this: `text-[rgb(var(--fg)/0.6)]` for 60 percent text, or `bg-[rgb(var(--accent))]` for the accent.

Rules for new code:
- Do not write hard-coded colours. Use the variables above.
- Do not put spaces inside Tailwind arbitrary values (`bg-[rgb(var(--accent)/0.1)]`, not `bg-[rgb(var(--accent) / 0.1)]`). A space splits the class and the colour silently fails.
- SVG attributes such as `fill` do not accept CSS variables. Use the `style` prop.

The landing hero (`components/originkit/hero-49.css`) has its own light overrides under `[data-theme="light"]`.

## 4. Shared pieces

| File | Purpose |
|---|---|
| `components/AppShell.tsx` | Header and navigation for signed-in pages. Provides `useUser()`. |
| `components/ThemeToggle.tsx` | Light and dark switch. Exports `useTheme()`. |
| `components/auth/SplitLayout.tsx` | Two-column layout (sage or blue panel and form), brand mark, emblem |
| `components/auth/styles.ts` | Shared class strings for auth forms, buttons, and alerts |
| `components/StatusPill.tsx` | Coloured label for counselling status |
| `components/SystemFacts.tsx` | Facts section on the landing page |
| `lib/api.ts` | `api()` fetch wrapper, token storage, shared TypeScript types, `apiBase()` |
| `lib/useAuth.ts` | Loads the current user and redirects visitors. Exports `destinationFor()`. |

## 5. Talking to the backend

`lib/api.ts` is the only place that calls `fetch`.

- `api<T>(path, { method, json })` sends JSON and parses the response.
- `apiBlob(path, ...)` returns a `Blob` (used for audio).
- Errors are thrown as `ApiError` with `status` and `detail`. A status of `0` means the server could not be reached.
- `apiBase()` uses `NEXT_PUBLIC_API_BASE_URL` if set. Otherwise it uses port 8000 on the host you opened the page from.

## 6. Hydration and the theme script

The theme script sets `data-theme` on `<html>` before React hydrates. The `<html>` tag has `suppressHydrationWarning` for this reason. Do not remove it.

## 7. Known limits

- Authenticated pages (`/talk`, `/sessions`, `/onboarding`) were checked by reading the code and building the project, not by screenshots, because they need a signed-in session.
- The PWA service worker only caches the home page and manifest.
- Tokens live in `localStorage`. See [status-and-known-issues.md](status-and-known-issues.md).

## 8. Commands

```bash
cd frontend
pnpm dev        # development server on port 3000
pnpm build      # production build
pnpm start -p 3000
pnpm lint
```
