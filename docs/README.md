# rafiki-chat: Documentation

Start here. Each document covers one part of the project.

| Document | What it covers |
|---|---|
| [getting-started.md](getting-started.md) | Install tools, set up the project, and run every service. Includes the backend command. |
| [architecture.md](architecture.md) | How the parts fit together, the request flow, and the safety pipeline. |
| [backend-api.md](backend-api.md) | Every API endpoint, with methods, auth requirements, and purpose. |
| [frontend.md](frontend.md) | Pages, user flows, the theme system, and shared components. |
| [mcp-server.md](mcp-server.md) | The MCP policy and tool server and its five tools. |
| [configuration.md](configuration.md) | Every environment variable, what it does, and its default. |
| [testing.md](testing.md) | How to run the test suites and what they cover. |
| [deployment.md](deployment.md) | Deploying the web app to Vercel, the API to Render, and the database on Neon. |
| [status-and-known-issues.md](status-and-known-issues.md) | What is built, what is placeholder, and known problems. |

## Quick reference

```bash
# Backend API (run from backend/, needs PostgreSQL running)
cd backend && uv run uvicorn app.main:app --reload --port 8000

# MCP tool server (run from mcp_server/)
cd mcp_server && uv run python -m campus_mcp.server

# Frontend (run from frontend/)
cd frontend && pnpm dev
```

The source of truth for product requirements is `Campus_Support_Companion_Architecture.pdf` in the project root.
