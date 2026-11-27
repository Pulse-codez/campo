"""study_planner — build study plans that respect mental health capacity."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

EnergyLevel = Literal["low", "moderate", "high"]


class StudyPlanInput(BaseModel):
    units: list[str] = Field(..., min_length=1, max_length=20, description="Course units or topics")
    hours_per_week: int = Field(..., ge=1, le=40, description="Available study hours per week")
    energy_level: EnergyLevel = Field("moderate", description="low | moderate | high")
    exam_weeks_away: int | None = Field(None, ge=1, le=52, description="Weeks until the next exam")

    @field_validator("units")
    @classmethod
    def units_must_not_be_blank(cls, values: list[str]) -> list[str]:
        if not all(value.strip() for value in values):
            raise ValueError("units must not contain empty strings")
        return values


class StudySession(BaseModel):
    day: str
    time: str
    duration_minutes: int
    unit: str
    activity: str
    break_minutes: int


class StudyPlanOutput(BaseModel):
    sessions: list[StudySession]
    total_hours: float
    notes: list[str]


DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MAX_SESSION_MINUTES = 120
CAPACITY_MULTIPLIER: dict[EnergyLevel, float] = {
    "low": 0.6,
    "moderate": 1.0,
    "high": 1.3,
}


def plan_study(
    units: list[str],
    hours_per_week: int,
    energy_level: str = "moderate",
    exam_weeks_away: int | None = None,
) -> StudyPlanOutput:
    """Generate a weekly plan paced by energy; session minutes sum to total_hours.

    This is a simple scheduler. Replace it with a real timetable/calendar
    integration before production use.
    """
    params = StudyPlanInput(
        units=units,
        hours_per_week=hours_per_week,
        energy_level=energy_level,
        exam_weeks_away=exam_weeks_away,
    )

    total_minutes = round(
        params.hours_per_week * CAPACITY_MULTIPLIER[params.energy_level] * 60
    )
    base_minutes, remainder = divmod(total_minutes, len(params.units))
    allocations = [
        base_minutes + (1 if index < remainder else 0)
        for index in range(len(params.units))
    ]

    sessions: list[StudySession] = []
    slot = 0
    for unit, minutes in zip(params.units, allocations):
        remaining = minutes
        while remaining > 0:
            duration = min(MAX_SESSION_MINUTES, remaining)
            sessions.append(
                StudySession(
                    day=DAYS[slot % len(DAYS)],
                    time=f"{9 + (slot % 8):02d}:00",
                    duration_minutes=duration,
                    unit=unit,
                    activity="Focused study with active recall",
                    break_minutes=10,
                )
            )
            remaining -= duration
            slot += 1

    total_hours = round(sum(s.duration_minutes for s in sessions) / 60, 2)
    notes = [
        f"Planned {total_hours:g} effective study hours this week.",
        "Take a 10-minute break every 50 minutes.",
        "If energy dips, switch to lighter review instead of skipping.",
    ]
    if params.energy_level == "low":
        notes.append("Prioritise sleep and one counselling check-in this week.")
    if params.exam_weeks_away and params.exam_weeks_away <= 2:
        notes.append("Exams are close — consider academic accommodation if needed.")

    return StudyPlanOutput(sessions=sessions, total_hours=total_hours, notes=notes)
