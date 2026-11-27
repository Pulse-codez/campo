"""Knowledge chunks embedded for semantic retrieval into Claude's context."""

import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.embedding import EMBEDDING_DIM
from app.models.base import ShortIdModel

if TYPE_CHECKING:
    from app.models.university import University


class KnowledgeChunk(ShortIdModel):
    __tablename__ = "knowledge_chunks"

    title: Mapped[str] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text())
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    # NULL means available to every campus; otherwise visible to one university.
    university_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("universities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )

    university: Mapped["University | None"] = relationship(back_populates="knowledge")
