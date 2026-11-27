"""Safety pipeline schemas."""

from pydantic import BaseModel, Field


class SafetyAssessment(BaseModel):
    level: str = Field(..., description="none | low | medium | high | crisis")
    requires_human: bool
    reasons: list[str] = []
    crisis_contacts: list[str] = []


class SafetyCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    previous_level: str | None = None
