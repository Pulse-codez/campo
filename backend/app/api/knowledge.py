"""Campus knowledge ingestion and semantic search for Claude."""

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DbSession, KnowledgeAdmin, McpActor
from app.schemas.knowledge import KnowledgeIn, KnowledgeOut
from app.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("", response_model=KnowledgeOut, status_code=201)
async def ingest(
    body: KnowledgeIn, db: DbSession, admin: KnowledgeAdmin
):
    return await knowledge_service.ingest(db, admin, body)


@router.get("", response_model=list[KnowledgeOut])
async def list_knowledge(db: DbSession, admin: KnowledgeAdmin):
    return await knowledge_service.list_chunks(db, admin)


@router.get("/search", response_model=list)
async def search_knowledge(
    db: DbSession,
    actor: McpActor,
    q: str = Query(..., min_length=1, max_length=500),
):
    university_id = actor.user.university_id if actor.user else None
    return await knowledge_service.search(db, q, university_id)


@router.delete("/{knowledge_id}", status_code=204)
async def delete_knowledge(knowledge_id: str, db: DbSession, admin: KnowledgeAdmin):
    if not await knowledge_service.remove(db, admin, knowledge_id):
        raise HTTPException(status_code=404, detail="knowledge_not_found")
