"""Study planner endpoint (delegates to MCP server)."""

from fastapi import APIRouter

from app.api.deps import McpActor
from app.schemas.study import StudyPlanRequest
from app.services.mcp_client import call_mcp_tool

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/plan")
async def plan_study(request: StudyPlanRequest, _actor: McpActor):
    return await call_mcp_tool(
        "plan_study",
        {
            "units": request.units,
            "hours_per_week": request.hours_per_week,
            "energy_level": request.energy_level,
            "exam_weeks_away": request.exam_weeks_away,
        },
    )
