"""Study planner schemas."""


from pydantic import BaseModel, Field


class StudyPlanRequest(BaseModel):
    units: list[str] = Field(..., min_items=1, max_items=20)
    hours_per_week: int = Field(..., ge=1, le=40)
    energy_level: str = Field("moderate", description="low | moderate | high")
    exam_weeks_away: int | None = Field(None, ge=1, le=52)
