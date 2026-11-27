"""Policy search endpoint (delegates to MCP server)."""

from fastapi import APIRouter, HTTPException

from app.services.mcp_client import MCPClient

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("/search")
async def search_policies(q: str, category: str | None = None, limit: int = 5):
    client = MCPClient()
    try:
        result = await client.call_tool(
            "search_policies",
            {"query": q, "category": category, "limit": limit},
        )
        return result
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"mcp_unavailable: {exc}") from exc
    finally:
        await client.close()
