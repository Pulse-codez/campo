"""User model. Every user belongs to one university."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ShortIdModel

if TYPE_CHECKING:
    from app.models.consent import ConsentRecord
    from app.models.conversation import Conversation
    from app.models.university import University

ROLES = ("student", "peer_counsellor", "counsellor", "admin")


class User(ShortIdModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(32), default="student", server_default="student")
    university_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("universities.id", ondelete="RESTRICT"), index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))

    # Broad, non-identifying profile used only for peer matching.
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    year_of_study: Mapped[int | None] = mapped_column(Integer, nullable=True)
    field_of_study: Mapped[str] = mapped_column(
        String(32), default="other", server_default=text("'other'")
    )
    # auto = opposite of the user's gender; male/female = explicit choice.
    voice_preference: Mapped[str] = mapped_column(
        String(16), default="auto", server_default=text("'auto'")
    )

    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    university: Mapped["University"] = relationship(back_populates="users")
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    consents: Mapped[list["ConsentRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
