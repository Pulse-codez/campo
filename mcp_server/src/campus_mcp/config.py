"""Runtime configuration for the FastMCP server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings read from `MCP_SERVER_*` environment variables."""

    host: str = "127.0.0.1"
    port: int = 8001
    path: str = "/mcp"
    stateless_http: bool = True
    auth_token: str = ""

    model_config = SettingsConfigDict(
        env_prefix="MCP_SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
