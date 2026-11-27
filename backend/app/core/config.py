"""Application configuration via pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The repo keeps one .env at the project root, not inside backend/.
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def normalise_database_url(url: str) -> str:
    """Make a PostgreSQL URL usable with the asyncpg driver.

    Accepts postgres:// and postgresql:// (as copied from Neon or other hosts), rewrites them to
    postgresql+asyncpg://, converts sslmode to asyncpg's ssl option, and drops channel_binding,
    which asyncpg does not support.
    """
    parts = urlsplit(url)
    scheme = parts.scheme
    if scheme in ("postgres", "postgresql"):
        scheme = "postgresql+asyncpg"
    query: list[tuple[str, str]] = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        if key == "sslmode":
            query.append(("ssl", value))
        elif key == "channel_binding":
            continue
        else:
            query.append((key, value))
    return urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "rafiki-chat"
    debug: bool = False
    sql_echo: bool = False

    database_url: str

    @field_validator("database_url")
    @classmethod
    def _normalise_database_url(cls, value: str) -> str:
        return normalise_database_url(value)

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 14

    # AES-GCM key for message bodies at rest. Derive 32 bytes with SHA-256.
    field_encryption_key: str = ""

    # When true, sign-up requires the campus email domain (and .ac.ke or .edu for "Other").
    # Off by default so any email can register. Turn on before a pilot (spec Section 11).
    enforce_university_email: bool = False

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"
    llm_timeout_seconds: int = 15

    elevenlabs_api_key: str = ""
    # Named voices: `auto` picks the opposite of the student's gender.
    elevenlabs_voice_id_female: str = ""
    elevenlabs_voice_id_male: str = ""
    # Legacy single voice, used only when a named voice is missing.
    elevenlabs_voice_id: str = ""
    elevenlabs_crisis_voice_id: str = ""
    elevenlabs_stt_model: str = "scribe_v1"
    elevenlabs_tts_model: str = "eleven_multilingual_v2"
    max_audio_bytes: int = 10 * 1024 * 1024

    # Vector knowledge for Claude. Postgres/pgvector is used when DATABASE_URL
    # points at Postgres; SQLite falls back to in-process cosine similarity.
    embedding_api_url: str = ""  # OpenAI-compatible /embeddings endpoint
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 384
    knowledge_top_k: int = 4

    mcp_server_url: str = "http://localhost:8001/mcp"
    mcp_timeout_seconds: float = 15.0
    mcp_auth_token: str = ""

    # Development: any localhost or private-network address on any port (for LAN testing).
    cors_origin_regex: str = r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3100",
        "http://127.0.0.1:3100",
    ]

    sentry_dsn: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = ""
    otel_exporter_otlp_endpoint: str = ""

    model_config = SettingsConfigDict(
        env_file=str(ROOT_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
