# Configuration

Settings come from environment variables and from `backend/.env`. Variables set in the shell take priority over the file.

## 1. Backend (`backend/.env`)

The backend reads these with pydantic-settings (`backend/app/core/config.py`). Names are case-insensitive.

| Variable | Default | Required | Purpose |
|---|---|---|---|
| `APP_ENV` | `development` | No | Environment label |
| `DEBUG` | `true` | No | Turns on SQL echo in logs. Set to `false` for quieter output. |
| `DATABASE_URL` | none | **Yes** | PostgreSQL URL, for example `postgresql+asyncpg://campus:campus@localhost:5432/campus_support`. Plain `postgresql://` or `postgres://` URLs are converted automatically, and Neon's `sslmode` and `channel_binding` parameters are translated (see `normalise_database_url` in `backend/app/core/config.py`). |
| `REDIS_URL` | `redis://localhost:6379/0` | No | Reserved for rate limiting. Not used yet. |
| `JWT_SECRET` | none | **Yes** | Signing key for tokens. Use a long random value outside development. |
| `JWT_ALGORITHM` | `HS256` | No | Token signing algorithm |
| `JWT_ACCESS_TTL_MINUTES` | `15` | No | Access token lifetime |
| `JWT_REFRESH_TTL_DAYS` | `14` | No | Refresh token lifetime |
| `ENFORCE_UNIVERSITY_EMAIL` | `false` | No | When `false`, any email can register. When `true`, the email must end with the chosen university's domain, and unlisted (`other`) universities need `.ac.ke` or `.edu`. Turn on before a pilot. |
| `FIELD_ENCRYPTION_KEY` | empty | No | Reserved for field-level encryption of message bodies. Not used yet. |
| `ANTHROPIC_API_KEY` | empty | For chat | Claude API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-5-5` | No | Model name. Options: `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-2`. |
| `LLM_TIMEOUT_SECONDS` | `15` | No | Timeout for model calls |
| `ELEVENLABS_API_KEY` | empty | For voice | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | empty | For voice | Voice used for normal replies |
| `ELEVENLABS_CRISIS_VOICE_ID` | empty | For voice | Calm voice for crisis replies |
| `ELEVENLABS_STT_MODEL` | `scribe_v1` | No | Speech-to-text model. Check the current ElevenLabs model name before pilot use. |
| `ELEVENLABS_TTS_MODEL` | `eleven_multilingual_v2` | No | Text-to-speech model. Check before pilot use. |
| `MCP_SERVER_URL` | `http://localhost:8001/mcp` | No | Address of the MCP tool server |
| `CORS_ORIGINS` | localhost and 127.0.0.1 on ports 3000 and 3100 | No | Exact allowed origins. JSON list, for example `["https://app.example.ac.ke"]`. |
| `CORS_ORIGIN_REGEX` | localhost and private network addresses, any port | No | Pattern for allowed origins. Suitable for development only. Remove or narrow it in production. |
| `SENTRY_DSN` | empty | No | Error reporting. Not wired up yet. |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` | empty | No | LLM tracing. Not wired up yet. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | empty | No | Tracing export. Not wired up yet. |

Setting names in the table are the environment variable names. In `.env`, write them in upper case as shown.

## 2. Frontend

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Port 8000 on the current host | Backend base URL. Put it in `frontend/.env.local`. Requires a restart after changes. |

`NEXT_PUBLIC_*` values are visible in the browser. Never put secrets in them.

## 3. MCP server

The MCP server takes no environment variables. Its host and port are set in `mcp_server/src/campus_mcp/server.py` (`127.0.0.1:8001`).

## 4. Root example file

`.env.example` at the project root lists the variables for every service, including ones not used yet. Copy it to start a new environment, then keep real secrets only in gitignored files.

## 5. Secrets

- `backend/.env` and `.env` files are gitignored. Do not commit them.
- Replace `JWT_SECRET` before anyone outside your machine uses the system.
- Rotate any key that was pasted into a chat, log, or ticket.
- The spec requires vendor keys to live in a secret manager in production (Section 11). Environment files are for development only.

## 6. Example `backend/.env`

```
DATABASE_URL=postgresql+asyncpg://campus:campus@localhost:5432/campus_support
JWT_SECRET=replace-with-a-long-random-string
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-5-5
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
ELEVENLABS_CRISIS_VOICE_ID=...
MCP_SERVER_URL=http://localhost:8001/mcp
DEBUG=false
```
