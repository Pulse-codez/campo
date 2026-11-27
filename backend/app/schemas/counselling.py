"""Counselling session schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SessionRequestIn(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255)
    preferred_time: str | None = Field(None, max_length=255)


class SessionUpdateIn(BaseModel):
    status: Literal["requested", "booked", "completed", "cancelled"]
    scheduled_at: datetime | None = None


class SessionOut(BaseModel):
    id: str
    student_name: str | None
    topic: str
    preferred_time: str | None
    scheduled_at: datetime | None
    status: str
    counsellor_id: str | None
    created_at: datetime
