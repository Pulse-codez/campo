"""MCP client tests using in-process and patched servers."""

from fastapi import HTTPException
from fastmcp import FastMCP

from app.services.mcp_client import MCPClient, call_mcp_tool

server = FastMCP("test-server")


@server.tool
def ping(value: str) -> str:
    return f"pong:{value}"


async def test_client_returns_structured_tool_data():
    result = await MCPClient(server).call_tool("ping", {"value": "hello"})

    assert result == "pong:hello"


async def test_call_mcp_tool_translates_failures_to_502(monkeypatch):
    async def fail(_self, _name, _arguments):
        raise RuntimeError("server offline")

    monkeypatch.setattr(MCPClient, "call_tool", fail)

    try:
        await call_mcp_tool("ping", {"value": "hello"})
    except HTTPException as exc:
        assert exc.status_code == 502
        assert exc.detail == "mcp_unavailable"
    else:
        raise AssertionError("expected HTTPException")
