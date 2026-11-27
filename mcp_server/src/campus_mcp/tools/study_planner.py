"""study_planner: build study plans that respect mental health capacity."""


from pydantic import BaseModel, Field


class StudyPlanInput(BaseModel):
    units: list[str] = Field(..., description="Course units or topics to study")
    hours_per_week: int = Field(..., ge=1, le=40, description="Available study hours per week")
    energy_level: str = Field(
        "moderate",
        description="Current energy/capacity: low, moderate, high",
    )
    exam_weeks_away: int | None = Field(
        None,
        ge=1,
        le=52,
        description="Weeks until the next major exam, if known",
    )


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


def plan_study(
    units: list[str],
    hours_per_week: int,
    energy_level: str = "moderate",
    exam_weeks_away: int | None = None,
) -> StudyPlanOutput:
    """Generate a weekly study plan that paces load by energy and exam proximity.

    Placeholder implementation. Replace with a real scheduler that integrates
    with the student's timetable and calendar before production.
    """
    capacity_multiplier = {"low": 0.6, "moderate": 1.0, "high": 1.3}.get(energy_level, 1.0)
    effective_hours = hours_per_week * capacity_multiplier
    per_unit = max(effective_hours / max(len(units), 1), 0.5)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sessions: list[StudySession] = []

    for i, unit in enumerate(units):
        day = days[i % 7]
        start_hour = 9 + (i % 8)
        duration = int(min(per_unit, 2) * 60)
        sessions.append(
            StudySession(
                day=day,
                time=f"{start_hour:02d}:00",
                duration_minutes=duration,
                unit=unit,
                activity="Focused study with active recall",
                break_minutes=10,
            )
        )

    notes = [
        f"Planned {effective_hours:.1f} effective study hours this week.",
        "Take a 10-minute break every 50 minutes.",
        "If energy dips, switch to lighter review instead of skipping.",
    ]
    if energy_level == "low":
        notes.append("Prioritise sleep and one counselling check-in this week.")
    if exam_weeks_away and exam_weeks_away <= 2:
        notes.append("Exams are close. Consider requesting academic accommodation if needed.")

    return StudyPlanOutput(sessions=sessions, total_hours=effective_hours, notes=notes)
