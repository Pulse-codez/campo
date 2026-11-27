"""Study planner endpoint (delegates to MCP server)."""

from fastapi import APIRouter, HTTPException

from app.schemas.study import StudyPlanRequest
from app.services.mcp_client import MCPClient

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/plan")
async def plan_study(request: StudyPlanRequest):
    client = MCPClient()
    try:
        result = await client.call_tool(
            "plan_study",
            {
                "units": request.units,
                "hours_per_week": request.hours_per_week,
                "energy_level": request.energy_level,
                "exam_weeks_away": request.exam_weeks_away,
            },
        )
        return result
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"mcp_unavailable: {exc}") from exc
    finally:
        await client.close()
