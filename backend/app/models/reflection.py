"""Monthly check-in: how the student is feeling and where they are heading."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import ShortIdModel


class MonthlyReflection(ShortIdModel):
    __tablename__ = "monthly_reflections"
    __table_args__ = (Index("uq_reflection_user_period", "user_id", "period", unique=True),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    period: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    feelings: Mapped[str] = mapped_column(Text)
    direction: Mapped[str] = mapped_column(Text)
