"""Policy search endpoint (delegates to MCP server)."""

from fastapi import APIRouter, Query

from app.api.deps import McpActor
from app.services.mcp_client import call_mcp_tool

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("/search")
async def search_policies(
    _actor: McpActor,  # registered account or anonymous token; RBAC enforced
    q: str = Query(..., min_length=1, max_length=500),
    category: str | None = None,
    limit: int = Query(5, ge=1, le=20),
):
    return await call_mcp_tool(
        "search_policies", {"query": q, "category": category, "limit": limit}
    )
