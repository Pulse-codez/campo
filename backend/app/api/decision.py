"""Decision lab endpoint (delegates to MCP server)."""

from fastapi import APIRouter, HTTPException

from app.schemas.decision import DecisionLabRequest
from app.services.mcp_client import MCPClient

router = APIRouter(prefix="/decision", tags=["decision"])


@router.post("/evaluate")
async def evaluate_decision(request: DecisionLabRequest):
    client = MCPClient()
    try:
        result = await client.call_tool(
            "evaluate_decision",
            {
                "situation": request.situation,
                "options": [o.model_dump() for o in request.options],
                "values": request.values,
            },
        )
        return result
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"mcp_unavailable: {exc}") from exc
    finally:
        await client.close()
