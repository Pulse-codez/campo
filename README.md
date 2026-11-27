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
cd mcp_server && uv run campus-mcp-server   # serves Streamable HTTP at /mcp

# Frontend
cd frontend && pnpm dev
cd frontend && pnpm lint

# Jobs
cd jobs && pnpm exec tsc --noEmit
```

## Conversation privacy and context

- Chats can be started without an account (`POST /conversations/anonymous`). The returned one-time token in `X-Anonymous-Token` is the only way back into that conversation; the server stores only its SHA-256 hash.
- Students may register/onboard with `gender`, `year_of_study` and a broad `field_of_study` (`tech`, `art`, `other`). `POST /peer/matches` pairs students by field and nearby year on a shared topic; peer messages are relayed only when neither student shows crisis language.
- Every message body is AES-GCM encrypted with `FIELD_ENCRYPTION_KEY` before it is stored (`v1:<nonce>:<ciphertext>`); reads decrypt transparently and legacy plaintext rows stay readable.
- Claude holds the conversation context for both typed and ElevenLabs voice turns. Each non-crisis turn fetches current policies and resources through MCP, runs pgvector semantic search over campus knowledge, and injects both into Claude's system context. Crisis turns bypass Claude, MCP and vector search entirely and return the fixed human-escalation protocol.
- Set the same token in `MCP_AUTH_TOKEN` (backend) and `MCP_SERVER_AUTH_TOKEN` (MCP server) whenever the tool server is reachable from outside localhost.

## IDs, roles and voices

- APIs exchange 5-character uppercase alphanumeric public IDs (for example `K7Q2M`). Internal UUID primary keys never leave the backend; legacy UUIDs still resolve during an upgrade.
- RBAC is centralised in `backend/app/core/rbac.py`: anonymous sessions may chat/match/use MCP tools; students may manage consent and request counselling; peer counsellors and counsellors manage the queue; only admins can change roles or ingest knowledge. Every route enforces the permission with a FastAPI dependency.
- ElevenLabs voices are named `ELEVENLABS_VOICE_ID_FEMALE` and `ELEVENLABS_VOICE_ID_MALE`. `voice_preference=auto` deliberately plays the **opposite** voice to the student's gender; `male`/`female` are explicit choices set through `PATCH /auth/me/voice` or the Talk screen. Crisis replies use `ELEVENLABS_CRISIS_VOICE_ID` when set.
- `EMBEDDING_API_URL` can point at any OpenAI-compatible embeddings endpoint. When unset, a deterministic local embedding is used so development and tests work offline. Admin users add knowledge with `POST /knowledge`; `GET /knowledge/search` is available to any authenticated or anonymous actor.

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
