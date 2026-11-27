"""Kind messages from Claude, and kind notes a student writes to someone."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.kind_note import KindNote
from app.schemas.kindness import KindMessageIn, KindMessageOut, KindNoteIn, KindNoteOut
from app.services.kindness_service import AIUnavailable, kind_message

router = APIRouter(prefix="/kindness", tags=["kindness"])


@router.post("/message", response_model=KindMessageOut)
async def generate_message(body: KindMessageIn, user: CurrentUser):
    try:
        text = await kind_message(body.theme)
    except AIUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return KindMessageOut(message=text, theme=body.theme)


@router.get("/notes", response_model=list[KindNoteOut])
async def list_notes(db: DbSession, user: CurrentUser):
    result = await db.execute(
        select(KindNote).where(KindNote.user_id == user.id).order_by(KindNote.created_at.desc())
    )
    return [KindNoteOut.model_validate(n) for n in result.scalars()]


@router.post("/notes", response_model=KindNoteOut, status_code=201)
async def create_note(body: KindNoteIn, db: DbSession, user: CurrentUser):
    note = KindNote(user_id=user.id, recipient=(body.recipient or "").strip() or None, body=body.body.strip())
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return KindNoteOut.model_validate(note)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: UUID, db: DbSession, user: CurrentUser):
    note = await db.get(KindNote, note_id)
    if note is None or note.user_id != user.id:
        raise HTTPException(status_code=404, detail="note_not_found")
    await db.delete(note)
    await db.commit()
