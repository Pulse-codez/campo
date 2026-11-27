"""University (tenant) model for the multi-university auth layer."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import ShortIdModel

if TYPE_CHECKING:
    from app.models.knowledge import KnowledgeChunk
    from app.models.user import User


class University(ShortIdModel):
    __tablename__ = "universities"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email_domains: Mapped[str] = mapped_column(String(512))  # comma-separated, e.g. "uonbi.ac.ke"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))

    users: Mapped[list["User"]] = relationship(back_populates="university")
    knowledge: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="university")

    @property
    def domains(self) -> list[str]:
        return [d.strip().lower() for d in self.email_domains.split(",") if d.strip()]
