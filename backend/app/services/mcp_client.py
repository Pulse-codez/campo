"""HTTP client for the FastMCP policy/tool server."""

import httpx

from app.core.config import get_settings

settings = get_settings()


class MCPClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.mcp_server_url
        self._client: httpx.AsyncClient | None = None

    async def _client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=15.0)
        return self._client

    async def call_tool(self, name: str, arguments: dict) -> dict:
        client = await self._client()
        resp = await client.post("/tools/call", json={"name": name, "arguments": arguments})
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
