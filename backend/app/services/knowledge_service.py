"""Semantic knowledge retrieval backed by pgvector (Postgres) or in-memory cosine (SQLite)."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.embedding import cosine_similarity, embed_texts
from app.models.base import new_public_id
from app.models.knowledge import KnowledgeChunk
from app.models.user import User
from app.schemas.knowledge import KnowledgeHit, KnowledgeIn, KnowledgeOut
from app.services.audit_service import audit
from app.services.id_service import find_by_public_id


def _excerpt(content: str, length: int = 400) -> str:
    return content if len(content) <= length else content[:length].rstrip() + "…"


def _hit(chunk: KnowledgeChunk, score: float) -> KnowledgeHit:
    return KnowledgeHit(
        id=chunk.public_id,
        title=chunk.title,
        source=chunk.source,
        excerpt=_excerpt(chunk.content),
        score=round(score, 4),
    )


def _visible(university_id: UUID | None):
    return or_(
        KnowledgeChunk.university_id.is_(None),
        KnowledgeChunk.university_id == university_id,
    )


async def ingest(db: AsyncSession, admin: User, body: KnowledgeIn) -> KnowledgeOut:
    vector = (await embed_texts([f"{body.title}\n{body.content}"]))[0]
    chunk = KnowledgeChunk(
        public_id=new_public_id(),
        title=body.title,
        content=body.content,
        source=body.source,
        embedding=vector,
        university_id=None if body.campus_wide else admin.university_id,
    )
    db.add(chunk)
    audit(db, admin.id, "knowledge.ingested", target=chunk.public_id)
    await db.commit()
    await db.refresh(chunk)
    return KnowledgeOut.from_chunk(chunk)


async def search(
    db: AsyncSession,
    query: str,
    university_id: UUID | None = None,
    limit: int | None = None,
) -> list[KnowledgeHit]:
    if not query.strip():
        return []
    top_k = limit or get_settings().knowledge_top_k
    vector = (await embed_texts([query]))[0]
    stmt = select(KnowledgeChunk).where(
        KnowledgeChunk.is_active.is_(True), _visible(university_id)
    )

    if db.get_bind().dialect.name == "postgresql":
        # pgvector does the cosine ranking inside Postgres using the HNSW index.
        distance = KnowledgeChunk.embedding.cosine_distance(vector)
        rows = (
            await db.execute(
                select(KnowledgeChunk, distance.label("distance"))
                .where(
                    KnowledgeChunk.is_active.is_(True), _visible(university_id)
                )
                .order_by(distance)
                .limit(top_k)
            )
        ).all()
        return [_hit(chunk, 1.0 - float(score)) for chunk, score in rows]

    # SQLite/dev fallback: the Vector type returns Python lists, so rank locally.
    chunks = (await db.execute(stmt)).scalars().all()
    scored = [(chunk, cosine_similarity(chunk.embedding or [], vector)) for chunk in chunks]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [_hit(chunk, score) for chunk, score in scored[:top_k]]


async def list_chunks(db: AsyncSession, admin: User) -> list[KnowledgeOut]:
    result = await db.execute(
        select(KnowledgeChunk)
        .where(KnowledgeChunk.is_active.is_(True), _visible(admin.university_id))
        .order_by(KnowledgeChunk.created_at.desc())
    )
    return [KnowledgeOut.from_chunk(chunk) for chunk in result.scalars().all()]


async def remove(db: AsyncSession, admin: User, public_id: str) -> bool:
    chunk = await find_by_public_id(db, KnowledgeChunk, public_id)
    if chunk is None or not (
        chunk.university_id is None or chunk.university_id == admin.university_id
    ):
        return False
    chunk.is_active = False
    audit(db, admin.id, "knowledge.removed", target=chunk.public_id)
    await db.commit()
    return True
