"""Study planner schemas."""

from typing import Literal

from pydantic import BaseModel, Field

EnergyLevel = Literal["low", "moderate", "high"]


class StudyPlanRequest(BaseModel):
    units: list[str] = Field(..., min_length=1, max_length=20)
    hours_per_week: int = Field(..., ge=1, le=40)
    energy_level: EnergyLevel = "moderate"
    exam_weeks_away: int | None = Field(None, ge=1, le=52)
