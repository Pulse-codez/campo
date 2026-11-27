"""Resource finder endpoint (delegates to MCP server)."""

from fastapi import APIRouter

from app.api.deps import McpActor
from app.schemas.resource import ResourceRequest
from app.services.mcp_client import call_mcp_tool

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/find")
async def find_resources(request: ResourceRequest, _actor: McpActor):
    return await call_mcp_tool(
        "find_resources",
        {
            "resource_type": request.resource_type,
            "location": request.location,
            "hours": request.hours,
        },
    )
