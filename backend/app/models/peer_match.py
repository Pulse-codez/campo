"""Peer support matches: students with shared field/issue, optionally anonymous."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ShortIdModel

if TYPE_CHECKING:
    from app.models.conversation import Conversation

PEER_STATUSES = ("searching", "matched", "closed")


class PeerMatch(ShortIdModel):
    __tablename__ = "peer_matches"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    counterpart_conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    seeker_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    peer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    topic: Mapped[str] = mapped_column(String(255))
    field_of_study: Mapped[str] = mapped_column(
        String(32), default="other", server_default=text("'other'"), index=True
    )
    year_of_study: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), default="searching", server_default=text("'searching'"), index=True
    )
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation: Mapped["Conversation"] = relationship(
        back_populates="peer_match",
        foreign_keys="[PeerMatch.conversation_id]",
    )
