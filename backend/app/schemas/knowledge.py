"""Schemas for the pgvector-backed campus knowledge base."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.models.knowledge import KnowledgeChunk


class KnowledgeIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=20000)
    source: str | None = Field(None, max_length=255)
    # Admin may share a document across all universities; default is own campus.
    campus_wide: bool = False


class KnowledgeOut(BaseModel):
    id: str
    title: str
    source: str | None
    content: str
    campus_wide: bool
    created_at: datetime

    @classmethod
    def from_chunk(cls, chunk: "KnowledgeChunk") -> "KnowledgeOut":
        return cls(
            id=chunk.public_id,
            title=chunk.title,
            source=chunk.source,
            content=chunk.content,
            campus_wide=chunk.university_id is None,
            created_at=chunk.created_at,
        )


class KnowledgeHit(BaseModel):
    id: str
    title: str
    source: str | None
    excerpt: str
    score: float
