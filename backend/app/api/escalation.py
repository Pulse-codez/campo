"""Escalation request endpoint (delegates to MCP server)."""

from fastapi import APIRouter

from app.api.deps import McpActor
from app.schemas.resource import EscalationRequest
from app.services.mcp_client import call_mcp_tool

router = APIRouter(prefix="/escalation", tags=["escalation"])


@router.post("/request")
async def request_escalation(request: EscalationRequest, _actor: McpActor):
    return await call_mcp_tool(
        "request_escalation",
        {
            "reason": request.reason,
            "urgency": request.urgency,
            "preferred_channel": request.preferred_channel,
        },
    )
