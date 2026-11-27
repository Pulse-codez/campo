"""Resource and escalation schemas."""


from pydantic import BaseModel, Field


class ResourceRequest(BaseModel):
    resource_type: str = Field(..., description="counselling | health_clinic | peer_support | emergency | legal_aid | other")
    location: str | None = None
    hours: str | None = None


class EscalationRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=5000)
    urgency: str = Field("routine", description="routine | urgent | crisis")
    preferred_channel: str | None = None
