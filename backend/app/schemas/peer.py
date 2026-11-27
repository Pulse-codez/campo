"""Peer matching schemas using short public IDs."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import StudyField

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.peer_match import PeerMatch


class PeerMatchCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255)
    field_of_study: StudyField = "other"
    year_of_study: int | None = Field(None, ge=1, le=10)
    anonymous: bool = False


class PeerMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    topic: str
    field_of_study: str
    year_of_study: int | None
    status: str
    matched_at: datetime | None
    peer_label: str | None = None
    anonymous_token: str | None = None

    @classmethod
    def from_match(
        cls,
        match: "PeerMatch",
        conversation_public_id: str,
        anonymous_token: str | None = None,
    ) -> "PeerMatchOut":
        peer_label = "A peer in your field" if match.status == "matched" else None
        return cls(
            id=match.public_id,
            conversation_id=conversation_public_id,
            topic=match.topic,
            field_of_study=match.field_of_study,
            year_of_study=match.year_of_study,
            status=match.status,
            matched_at=match.matched_at,
            peer_label=peer_label,
            anonymous_token=anonymous_token,
        )


class PeerMessageIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class PeerMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime

    @classmethod
    def from_message(cls, message: "Message", content: str) -> "PeerMessageOut":
        return cls(
            id=message.public_id,
            role=message.role,
            content=content,
            created_at=message.created_at,
        )
