"""Conversation model. AI and peer conversations share the same encrypted store."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ShortIdModel

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.peer_match import PeerMatch
    from app.models.user import User


class Conversation(ShortIdModel):
    __tablename__ = "conversations"

    # Nullable for anonymous sessions; ownership is proven by a token hash.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )
    anonymous_token_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    mode: Mapped[str] = mapped_column(
        String(16), default="ai", server_default=text("'ai'")
    )  # ai | peer
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))

    user: Mapped["User | None"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    peer_match: Mapped["PeerMatch | None"] = relationship(
        back_populates="conversation",
        uselist=False,
        foreign_keys="[PeerMatch.conversation_id]",
    )
