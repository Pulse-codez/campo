"""Auth request/response schemas."""

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    from app.models.user import User

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say"]
StudyField = Literal["tech", "art", "other"]
VoicePreference = Literal["auto", "male", "female"]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: str | None = Field(None, max_length=255)
    university_id: str = Field(..., min_length=5, max_length=36)
    other_university_name: str | None = Field(None, max_length=255)
    gender: Gender | None = None
    year_of_study: int | None = Field(None, ge=1, le=10)
    field_of_study: StudyField = "other"
    voice_preference: VoicePreference = "auto"


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    email: str
    full_name: str | None
    role: str
    university_id: str
    onboarded: bool
    gender: Gender | None = None
    year_of_study: int | None = None
    field_of_study: StudyField = "other"
    voice_preference: VoicePreference = "auto"
    concerns: list[str] = Field(default_factory=list, validation_alias="concerns_list")
    therapist_key: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    @classmethod
    def from_user(cls, user: "User") -> "UserOut":
        """Serialise a user with short public IDs, never internal UUIDs."""
        return cls(
            id=user.public_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            university_id=user.university.public_id if user.university else str(user.university_id),
            onboarded=user.onboarded,
            gender=user.gender,  # type: ignore[arg-type]
            year_of_study=user.year_of_study,
            field_of_study=user.field_of_study,  # type: ignore[arg-type]
            voice_preference=user.voice_preference,  # type: ignore[arg-type]
            concerns=user.concerns_list,
            therapist_key=user.therapist_key,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )


class VoicePreferenceIn(BaseModel):
    preference: VoicePreference
