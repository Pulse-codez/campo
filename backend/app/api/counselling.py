"""Counselling sessions: students request, staff accept and close."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbSession, StaffUser
from app.schemas.counselling import SessionOut, SessionRequestIn, SessionUpdateIn
from app.services import counselling_service
from app.services.consent_service import has_consent

router = APIRouter(prefix="/counselling-sessions", tags=["counselling"])


@router.get("", response_model=list[SessionOut])
async def list_sessions(db: DbSession, user: CurrentUser):
    if user.role == "student":
        return await counselling_service.list_for_student(db, user)
    return await counselling_service.list_for_staff(db, user)


@router.post("", response_model=SessionOut, status_code=201)
async def request_session(body: SessionRequestIn, db: DbSession, user: CurrentUser):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="students_only")
    if not await has_consent(db, user.id, "counselling"):
        raise HTTPException(status_code=403, detail="counselling_consent_required")
    return await counselling_service.create_request(db, user, body.topic, body.preferred_time)


@router.patch("/{session_id}", response_model=SessionOut)
async def update_session(session_id: UUID, body: SessionUpdateIn, db: DbSession, staff: StaffUser):
    updated = await counselling_service.update_status(
        db, staff, session_id, body.status, body.scheduled_at
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return updated
