"""Counselling session requests and bookings for students."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import ShortIdModel

SESSION_STATUSES = ("requested", "booked", "completed", "cancelled")


class CounsellingSession(ShortIdModel):
    __tablename__ = "counselling_sessions"

    university_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("universities.id", ondelete="RESTRICT"), index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    counsellor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    topic: Mapped[str] = mapped_column(String(255))
    preferred_time: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="requested", server_default="requested")
