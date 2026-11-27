# Getting started

This guide takes you from a fresh clone to all services running.

## 1. Prerequisites

| Tool | Version used | Used for |
|---|---|---|
| Python | 3.12 or newer | Backend and MCP server (managed by uv) |
| uv | 0.13 or newer | Python packages and running Python code |
| Node.js | 20 or newer | Frontend |
| pnpm | 9 or newer | Node packages (we do not use npm) |
| PostgreSQL | 16 | Application database |
| Redis | 7 | Planned for rate limiting (not used yet, optional) |

Docker is not used in this project.

## 2. Install a PostgreSQL database

Install PostgreSQL 16 with your operating system's package manager, or any other method you prefer. Then create the database the backend expects:

```bash
sudo -u postgres psql -c "CREATE USER campus WITH PASSWORD 'campus';"
sudo -u postgres psql -c "CREATE DATABASE campus_support OWNER campus;"
```

The default connection string is in `backend/.env`:

```
DATABASE_URL=postgresql+asyncpg://campus:campus@localhost:5432/campus_support
```

Change it there if your database uses different credentials or a different host.

## 3. Install dependencies

```bash
cd backend && uv sync          # Python dependencies for the API
cd ../mcp_server && uv sync    # Python dependencies for the MCP tool server
cd ../frontend && pnpm install # Node dependencies for the web app
cd ../jobs && pnpm install     # Node dependencies for background jobs (not running yet)
```

## 4. Configure environment files

| File | Purpose | Committed? |
|---|---|---|
| `backend/.env` | Backend settings, including secrets | No (gitignored) |
| `.env.example` | Template listing every variable | Yes |

`backend/.env` already exists for local development. Before using real data, replace `JWT_SECRET` with a long random value, and add `ANTHROPIC_API_KEY` and the ElevenLabs keys if you want the chat and voice features to call those services. See [configuration.md](configuration.md).

## 5. Run the services

Run each service in its own terminal.

### Backend API (FastAPI)

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

On startup the backend creates any missing tables and seeds the university list. Check it is up:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/universities
```

Interactive API documentation is at `http://localhost:8000/docs`.

### MCP tool server (FastMCP)

```bash
cd mcp_server
uv run python -m campus_mcp.server
```

It listens on `http://127.0.0.1:8001/mcp`. The backend calls it for resource lookup, study planning, decision support, policy search, and escalation requests. Those routes return an error if this server is not running.

### Frontend (Next.js)

```bash
cd frontend
pnpm dev
```

Open `http://localhost:3000`. The frontend talks to the backend on port 8000 of the same host you opened the page from. To point it elsewhere, set `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local`.

For a production-style run:

```bash
cd frontend && pnpm build && pnpm start -p 3000
```

### Background jobs (trigger.dev)

Not running yet. The `jobs/` folder contains a placeholder only. See [status-and-known-issues.md](status-and-known-issues.md).

## 6. First use

1. Open the site and choose **Sign up**, or go to `/login?tab=new`.
2. Pick your university. Enter your university email (for example `you@uonbi.ac.ke`) and a password of at least 8 characters.
3. Sign in on the **Sign in** tab.
4. Complete onboarding: choose what is on your mind, pick a virtual therapist, and set privacy choices.
5. You land on the chat at `/talk`.

To try counsellor features, an admin must first give a user a staff role. The admin endpoint is `PATCH /admin/users/{user_id}/role`. There is no admin screen yet. See [backend-api.md](backend-api.md).

## 7. Common problems

| Symptom | Cause and fix |
|---|---|
| `Cannot reach the server at http://...:8000` on the sign-up page | The backend is not running. Start it with the command in step 5. |
| Backend exits at startup with a connection error | PostgreSQL is not running, or `DATABASE_URL` in `backend/.env` is wrong. |
| University dropdown says it could not load | Same as above. Use the **Try again** button after the backend is up. |
| Chat replies fail or show an error | `ANTHROPIC_API_KEY` is missing or invalid. Crisis messages still work without it. |
| Voice button says voice is unavailable | ElevenLabs keys are not set. Typing still works. |
| Resource, study, decision, or policy routes return 502 | The MCP server on port 8001 is not running. |
| Browser shows a hydration warning | Usually a browser extension rewriting the page. The theme script is already handled. |

## 8. Useful commands

```bash
cd backend && uv run pytest          # backend tests
cd backend && uv run ruff check .    # backend lint
cd frontend && pnpm lint             # frontend lint
cd frontend && pnpm build            # frontend production build
cd mcp_server && uv run ruff check . # MCP lint
```
