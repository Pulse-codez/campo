# Deployment

rafiki-chat has two deployable parts:

| Part | Where | Config file |
|---|---|---|
| Web app (Next.js) | Vercel | Set `NEXT_PUBLIC_API_BASE_URL` (see below) |
| API (FastAPI) | Render | `render.yaml` at the repository root |
| Database | Neon (PostgreSQL with pgvector) | `DATABASE_URL` on Render |
| Tools server (MCP) | Not deployed yet | `MCP_SERVER_URL` on Render |

## 1. Database (Neon)

1. In the Neon dashboard, open the project, then **Connection details**, and copy the full string.
2. Reset the password first if it has ever been shared or pasted into a log.
3. The API enables the `vector` extension on startup. To check it manually, run this in the Neon SQL editor:
   ```sql
   SELECT extname FROM pg_extension WHERE extname = 'vector';
   ```
   An empty result means the extension is not enabled yet. The API creates it on its first start.

## 2. API (Render)

1. In Render, choose **New** then **Blueprint**, and select this repository. Render reads `render.yaml`.
2. Fill in the values marked as secrets in the dashboard:
   - `DATABASE_URL`: the full Neon string, starting with `postgresql://`. The API converts it automatically.
   - `ANTHROPIC_API_KEY`, and the `ELEVENLABS_*` keys if you use voice.
   - `CORS_ORIGINS`: your Vercel address, for example `["https://rafiki-chat.vercel.app"]`. Edit this in the blueprint, or in the dashboard.
3. Deploy. The start command is `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

### Checking the deploy

| Stage | What you should see |
|---|---|
| Build log | `uv sync` finishes without errors |
| Start log | `Application startup complete.` and no tracebacks |
| `GET /health` | `{"status":"ok", ...}` |
| `GET /universities` | The list of universities |

If startup fails, read the first `Error` line in the log, not the last one. The common causes are:

| Message | Cause and fix |
|---|---|
| `password authentication failed for user 'npg_...'` | `DATABASE_URL` has the password in the username position. Paste the whole string from Neon. |
| `type "vector" does not exist` | The `vector` extension is not enabled. The API creates it on start; if that fails, run `CREATE EXTENSION IF NOT EXISTS vector;` in the Neon SQL editor. |
| `Field required` for `jwt_secret` or `database_url` | A required variable is missing. Check the Environment tab. |
| `No open ports detected` | The app crashed before it started listening. Read the traceback above it. |

## 3. Web app (Vercel)

1. Import the repository, and set the root directory to `frontend`.
2. Add one environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` = the Render address, for example `https://rafiki-chat-api.onrender.com`
3. Redeploy after any change, because `NEXT_PUBLIC_` values are built into the app.

## 4. Things to change before a pilot

- Set `ENFORCE_UNIVERSITY_EMAIL` to `true` after the domains are verified.
- Replace the placeholder `CORS_ORIGINS` value with your real Vercel address.
- Add Alembic migrations, then set `APP_ENV` to `production`.
- Deploy the MCP tools server, then set `MCP_SERVER_URL`.
