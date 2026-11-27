"""Decision lab endpoint (delegates to MCP server)."""

from fastapi import APIRouter

from app.api.deps import McpActor
from app.schemas.decision import DecisionLabRequest
from app.services.mcp_client import call_mcp_tool

router = APIRouter(prefix="/decision", tags=["decision"])


@router.post("/evaluate")
async def evaluate_decision(request: DecisionLabRequest, _actor: McpActor):
    return await call_mcp_tool(
        "evaluate_decision",
        {
            "situation": request.situation,
            "options": [o.model_dump() for o in request.options],
            "values": request.values,
        },
    )
