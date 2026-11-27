"""Resource finder endpoint (delegates to MCP server)."""

from fastapi import APIRouter, HTTPException

from app.schemas.resource import ResourceRequest
from app.services.mcp_client import MCPClient

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/find")
async def find_resources(request: ResourceRequest):
    client = MCPClient()
    try:
        result = await client.call_tool(
            "find_resources",
            {
                "resource_type": request.resource_type,
                "location": request.location,
                "hours": request.hours,
            },
        )
        return result
    except Exception as exc:  # pragma: no cover - MCP may be offline in dev
        raise HTTPException(status_code=502, detail=f"mcp_unavailable: {exc}") from exc
    finally:
        await client.close()
