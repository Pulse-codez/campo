"""Client for the FastMCP policy/tool server, using the MCP protocol."""

import logging
from typing import Any

from fastapi import HTTPException
from fastmcp import Client, FastMCP
from fastmcp.client.auth import BearerAuth

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Speak MCP to the tool server. `source` may be a URL or in-process server."""

    def __init__(self, source: str | FastMCP | None = None, timeout: float | None = None):
        settings = get_settings()
        self.source = source or settings.mcp_server_url
        self.timeout = settings.mcp_timeout_seconds if timeout is None else timeout

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        auth = (
            BearerAuth(get_settings().mcp_auth_token)
            if isinstance(self.source, str) and get_settings().mcp_auth_token
            else None
        )
        async with Client(self.source, timeout=self.timeout, auth=auth) as client:
            result = await client.call_tool(name, arguments)
            return result.data

    async def close(self) -> None:
        # Each call opens and closes its own connection.
        return None


async def call_mcp_tool(name: str, arguments: dict[str, Any]) -> Any:
    """REST proxy helper: translate MCP failures into a clean 502."""
    try:
        return await MCPClient().call_tool(name, arguments)
    except Exception as exc:
        logger.exception("MCP tool %s failed", name)
        raise HTTPException(status_code=502, detail="mcp_unavailable") from exc
