"""Versioned, append-only consent records (spec Section 11)."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampedModel

if TYPE_CHECKING:
    from app.models.user import User

CONSENT_SCOPES = ("counselling", "emergency_contact", "research", "analytics")


class ConsentRecord(TimestampedModel):
    __tablename__ = "consent_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    scope: Mapped[str] = mapped_column(String(32))
    granted: Mapped[bool] = mapped_column(Boolean)
    policy_version: Mapped[str] = mapped_column(String(16))

    user: Mapped["User"] = relationship(back_populates="consents")
