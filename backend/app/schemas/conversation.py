"""Conversation and message schemas using short public IDs."""

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import StudyField

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.message import Message


class ConversationCreate(BaseModel):
    title: str | None = Field(None, max_length=255)
    mode: Literal["ai", "peer"] = "ai"


class AnonymousConversationCreate(BaseModel):
    """No account required; an opaque token is returned once."""

    title: str | None = Field(None, max_length=255)
    field_of_study: StudyField = "other"
    year_of_study: int | None = Field(None, ge=1, le=10)


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str | None
    is_archived: bool
    mode: str = "ai"
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_conversation(cls, conversation: "Conversation") -> "ConversationOut":
        return cls(
            id=conversation.public_id,
            title=conversation.title,
            is_archived=conversation.is_archived,
            mode=conversation.mode,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )


class AnonymousConversationOut(ConversationOut):
    anonymous_token: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    risk_level: str | None
    created_at: datetime

    @classmethod
    def from_message(cls, message: "Message", content: str) -> "MessageOut":
        return cls(
            id=message.public_id,
            role=message.role,
            content=content,
            risk_level=message.risk_level,
            created_at=message.created_at,
        )


class ChatRequest(BaseModel):
    conversation_id: str | None = Field(None, min_length=5, max_length=36)
    message: str = Field(..., min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    assistant_content: str
    risk_level: str
    requires_human: bool
    mode: str = "ai"
    crisis_contacts: list[str] = Field(default_factory=list)
    safety_reasons: list[str] = Field(default_factory=list)
    ticket_id: str | None = None


class VoiceTurnResponse(BaseModel):
    transcript: str
    turn: ChatResponse
