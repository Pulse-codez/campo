"""Kind messages from Claude, and kind notes a student writes to someone."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.kind_note import KindNote
from app.schemas.kindness import KindMessageIn, KindMessageOut, KindNoteIn, KindNoteOut
from app.services.kindness_service import AIUnavailable, kind_message

router = APIRouter(prefix="/kindness", tags=["kindness"])


def _out(note: KindNote) -> KindNoteOut:
    """Only the short public ID leaves the API; the UUID stays internal."""
    return KindNoteOut(
        id=note.public_id,
        recipient=note.recipient,
        body=note.body,
        created_at=note.created_at,
    )


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
    return [_out(n) for n in result.scalars()]


@router.post("/notes", response_model=KindNoteOut, status_code=201)
async def create_note(body: KindNoteIn, db: DbSession, user: CurrentUser):
    note = KindNote(user_id=user.id, recipient=(body.recipient or "").strip() or None, body=body.body.strip())
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return _out(note)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: str, db: DbSession, user: CurrentUser):
    note = await db.scalar(
        select(KindNote).where(KindNote.public_id == note_id, KindNote.user_id == user.id)
    )
    if note is None:
        raise HTTPException(status_code=404, detail="note_not_found")
    await db.delete(note)
    await db.commit()
