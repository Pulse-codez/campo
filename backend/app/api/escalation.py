"""Escalation request endpoint (delegates to MCP server)."""

from fastapi import APIRouter, HTTPException

from app.schemas.resource import EscalationRequest
from app.services.mcp_client import MCPClient

router = APIRouter(prefix="/escalation", tags=["escalation"])


@router.post("/request")
async def request_escalation(request: EscalationRequest):
    client = MCPClient()
    try:
        result = await client.call_tool(
            "request_escalation",
            {
                "reason": request.reason,
                "urgency": request.urgency,
                "preferred_channel": request.preferred_channel,
            },
        )
        return result
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"mcp_unavailable: {exc}") from exc
    finally:
        await client.close()
