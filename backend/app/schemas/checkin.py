"""Monthly check-in schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CheckinIn(BaseModel):
    period: str | None = Field(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    feelings: str = Field(..., min_length=1, max_length=4000)
    direction: str = Field(..., min_length=1, max_length=4000)


class CheckinOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    period: str
    feelings: str
    direction: str
    created_at: datetime


class CheckinResult(BaseModel):
    entry: CheckinOut
    requires_human: bool
    contacts: list[str] = []


class CheckinStatus(BaseModel):
    current_period: str
    open_periods: list[str]
    submitted_periods: list[str]
