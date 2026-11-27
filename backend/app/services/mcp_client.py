"""Client for the FastMCP policy/tool server, using the MCP protocol."""

from typing import Any

from fastmcp import Client

from app.core.config import get_settings


class MCPClient:
    def __init__(self, url: str | None = None):
        self.url = url or get_settings().mcp_server_url

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async with Client(self.url) as client:
            result = await client.call_tool(name, arguments)
            return result.structured_content or result.data

    async def close(self) -> None:
        # Each call opens and closes its own connection; kept so route handlers stay simple.
        return None
