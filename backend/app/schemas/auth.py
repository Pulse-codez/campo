"""Auth request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: str | None = Field(None, max_length=255)
    university_id: UUID
    other_university_name: str | None = Field(None, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    role: str
    university_id: UUID
    onboarded: bool
    concerns: list[str] = Field(default_factory=list, validation_alias="concerns_list")
    therapist_key: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime
