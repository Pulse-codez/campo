"""Counselling session requests, queue, and status changes. Scoped to one university."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.counselling_session import CounsellingSession
from app.models.user import User
from app.schemas.counselling import SessionOut
from app.services.audit_service import audit
from app.services.consent_service import has_consent

STAFF_ROLES = ("peer_counsellor", "counsellor", "admin")


def _to_out(session: CounsellingSession, student_name: str | None) -> SessionOut:
    return SessionOut(
        id=session.id,
        student_name=student_name,
        topic=session.topic,
        preferred_time=session.preferred_time,
        scheduled_at=session.scheduled_at,
        status=session.status,
        counsellor_id=session.counsellor_id,
        created_at=session.created_at,
    )


async def list_for_student(db: AsyncSession, student: User) -> list[SessionOut]:
    result = await db.execute(
        select(CounsellingSession)
        .where(CounsellingSession.student_id == student.id)
        .order_by(CounsellingSession.created_at.desc())
    )
    return [_to_out(s, student.full_name) for s in result.scalars()]


async def list_for_staff(db: AsyncSession, staff: User) -> list[SessionOut]:
    result = await db.execute(
        select(CounsellingSession, User.full_name, User.id)
        .join(User, User.id == CounsellingSession.student_id)
        .where(CounsellingSession.university_id == staff.university_id)
        .order_by(CounsellingSession.created_at.desc())
    )
    out: list[SessionOut] = []
    for session, student_name, student_id in result.all():
        if session.counsellor_id not in (None, staff.id):
            continue
        # Counsellors only see students who have consented to counselling (spec Section 11).
        if not await has_consent(db, student_id, "counselling"):
            continue
        out.append(_to_out(session, student_name))
    return out


async def create_request(
    db: AsyncSession, student: User, topic: str, preferred_time: str | None
) -> SessionOut:
    session = CounsellingSession(
        university_id=student.university_id,
        student_id=student.id,
        topic=topic,
        preferred_time=preferred_time,
        status="requested",
    )
    db.add(session)
    audit(db, student.id, "counselling.requested", target=str(session.id))
    await db.commit()
    await db.refresh(session)
    return _to_out(session, student.full_name)


async def update_status(
    db: AsyncSession,
    staff: User,
    session_id: UUID,
    status: str,
    scheduled_at,
) -> SessionOut | None:
    session = await db.get(CounsellingSession, session_id)
    if session is None or session.university_id != staff.university_id:
        return None
    if session.counsellor_id not in (None, staff.id):
        return None

    if status == "booked" and session.counsellor_id is None:
        session.counsellor_id = staff.id
    session.status = status
    if scheduled_at is not None:
        session.scheduled_at = scheduled_at

    audit(db, staff.id, f"counselling.{status}", target=str(session.id))
    await db.commit()
    await db.refresh(session)
    student = await db.get(User, session.student_id)
    return _to_out(session, student.full_name if student else None)
