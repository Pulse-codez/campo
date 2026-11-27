"""Application configuration via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "campus-support-companion"
    debug: bool = True

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 14

    field_encryption_key: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"
    llm_timeout_seconds: int = 15

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_crisis_voice_id: str = ""
    elevenlabs_stt_model: str = "scribe_v1"
    elevenlabs_tts_model: str = "eleven_multilingual_v2"

    mcp_server_url: str = "http://localhost:8001/mcp"

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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
