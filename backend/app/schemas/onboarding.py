"""Onboarding and consent schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OnboardingIn(BaseModel):
    concerns: list[str] = Field(default_factory=list, max_length=10)
    therapist_key: str | None = Field(None, max_length=32)
    consents: dict[str, bool] = Field(default_factory=dict)
    emergency_contact_name: str | None = Field(None, max_length=255)
    emergency_contact_phone: str | None = Field(None, max_length=32)
    policy_version: str = Field("v1.0", max_length=16)


class ConsentIn(BaseModel):
    scope: str
    granted: bool
    policy_version: str = Field("v1.0", max_length=16)


class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scope: str
    granted: bool
    policy_version: str
    updated_at: datetime
