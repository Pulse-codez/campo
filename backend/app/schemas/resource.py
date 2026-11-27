"""Resource and escalation schemas."""

from typing import Literal

from pydantic import BaseModel, Field

ResourceType = Literal[
    "counselling",
    "health_clinic",
    "peer_support",
    "emergency",
    "spiritual",
    "legal_aid",
    "other",
]
Urgency = Literal["routine", "urgent", "crisis"]
PreferredChannel = Literal[
    "counselling", "health_clinic", "peer_support", "security", "other"
]


class ResourceRequest(BaseModel):
    resource_type: ResourceType
    location: str | None = Field(None, max_length=255)
    hours: str | None = Field(None, max_length=255)


class EscalationRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=5000)
    urgency: Urgency = "routine"
    preferred_channel: PreferredChannel | None = None
