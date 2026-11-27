# Campus Support Companion

Peer-style support tool for university students in Kenya. Specification: `Campus_Support_Companion_Architecture.pdf` (v1.0).

Scope for v1.0: PWA client, FastAPI backend, Claude (Anthropic API) behind an LLM adapter, ElevenLabs speech, FHIR R4 facade, FastMCP policy/tool server, trigger.dev background jobs. AWS hosting and native apps are excluded.

## Layout

| Path | Purpose | Tooling |
|---|---|---|
| `frontend/` | PWA client (Next.js, service worker, IndexedDB, Web Push) | pnpm |
| `backend/` | FastAPI gateway, safety pipeline, LangGraph orchestrator, LLM adapter, FHIR facade | uv |
| `mcp_server/` | FastMCP server: policy_search, resource_finder, study_planner, decision_lab, escalation_request | uv |
| `jobs/` | trigger.dev jobs: escalation chains, follow-ups, retention deletion, analytics | pnpm |
| `infra/` | Deployment and infrastructure config (reserved) | |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager, Python 3.12+)
- [pnpm](https://pnpm.io/) (Node package manager)
- Node.js 20+
- PostgreSQL 16 and Redis 7, installed locally or reachable at the URLs in `.env`

## First-time setup

```bash
cp .env.example .env              # then fill in secrets

cd backend && uv sync             # Python deps (creates .venv)
cd ../mcp_server && uv sync
cd ../frontend && pnpm install
cd ../jobs && pnpm install
```

## Common commands

```bash
# Backend
cd backend && uv run fastapi dev app/main.py
cd backend && uv run alembic upgrade head
cd backend && uv run pytest
cd backend && uv run ruff check .

# MCP server
cd mcp_server && uv run pytest

# Frontend
cd frontend && pnpm dev
cd frontend && pnpm lint

# Jobs
cd jobs && pnpm exec tsc --noEmit
```

## Principles (from spec Section 1)

1. A student in immediate danger always reaches a human or emergency service, regardless of model behavior or network conditions.
2. Sensitive health data is auditable, consented, and minimal.
3. The conversational layer is replaceable. Vendor SDKs are imported only inside the LLM adapter.

## Open items before build (spec Section 3)

- Conversation model is Claude via the Anthropic API (replaces TheraBot). Confirm in writing with Anthropic: data residency, retention, use of conversation data for training, deletion on request, and a data processing agreement that fits the Kenya Data Protection Act 2019. Confirm the suitability of the model for crisis-adjacent use.
- Choose the model. Options: `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-2`. Set `ANTHROPIC_MODEL` in `.env`. The default is `claude-sonnet-5-5`.
- Confirm ElevenLabs audio retention, residency, and latency from Kenya.
- Clinical sign-off on risk taxonomy, escalation matrix, screening instruments, and crisis templates.
- Regulatory review: Kenya Data Protection Act 2019, Digital Health Act 2023.
