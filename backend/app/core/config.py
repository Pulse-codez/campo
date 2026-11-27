"""Application configuration via pydantic-settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The repo keeps one .env at the project root, not inside backend/.
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "campus-support-companion"
    debug: bool = False
    sql_echo: bool = False

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 14

    # AES-GCM key for message bodies at rest. Derive 32 bytes with SHA-256.
    field_encryption_key: str = ""

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
