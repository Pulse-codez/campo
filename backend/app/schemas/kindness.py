"""Kind messages and kind notes schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

KindTheme = Literal["encouragement", "hope", "rest", "self_kindness"]


class KindMessageIn(BaseModel):
    theme: KindTheme = "encouragement"


class KindMessageOut(BaseModel):
    message: str
    theme: KindTheme


class KindNoteIn(BaseModel):
    recipient: str | None = Field(None, max_length=120)
    body: str = Field(..., min_length=1, max_length=2000)


class KindNoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient: str | None
    body: str
    created_at: datetime
