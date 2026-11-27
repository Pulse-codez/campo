"""Monthly check-in: feelings and direction, once per month, in the last week of the month."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.reflection import MonthlyReflection
from app.safety.classifier import assess
from app.schemas.checkin import CheckinIn, CheckinOut, CheckinResult, CheckinStatus
from app.services.audit_service import audit
from app.services.checkin_service import check_writable, period_of, writable_periods

router = APIRouter(prefix="/checkin", tags=["checkin"])

CRISIS_CONTACTS = [
    "National mental health helpline: 1199 (24/7, free)",
    "Campus security: +254 700 000 999 (on campus, 24/7)",
    "Nearest hospital emergency department",
]


def _today() -> datetime:
    return datetime.now(UTC)


async def _submitted(db, user_id: UUID) -> set[str]:
    result = await db.execute(select(MonthlyReflection.period).where(MonthlyReflection.user_id == user_id))
    return set(result.scalars().all())


@router.get("/status", response_model=CheckinStatus)
async def status(db: DbSession, user: CurrentUser):
    today = _today().date()
    submitted = await _submitted(db, user.id)
    return CheckinStatus(
        current_period=period_of(today),
        open_periods=writable_periods(today, submitted),
        submitted_periods=sorted(submitted, reverse=True),
    )


@router.get("", response_model=list[CheckinOut])
async def list_checkins(db: DbSession, user: CurrentUser):
    result = await db.execute(
        select(MonthlyReflection)
        .where(MonthlyReflection.user_id == user.id)
        .order_by(MonthlyReflection.period.desc())
    )
    return [
        CheckinOut(
            id=str(r.id),
            period=r.period,
            feelings=r.feelings,
            direction=r.direction,
            created_at=r.created_at,
        )
        for r in result.scalars()
    ]


@router.post("", response_model=CheckinResult, status_code=201)
async def submit_checkin(body: CheckinIn, db: DbSession, user: CurrentUser):
    today = _today().date()
    period = body.period or period_of(today)
    submitted = await _submitted(db, user.id)
    check = check_writable(period, today, submitted)
    if not check.allowed:
        status_code = 409 if check.reason == "already_submitted" else 422
        raise HTTPException(status_code=status_code, detail=check.reason)

    # The entry is saved either way. A crisis reply tells the app to show human contacts.
    crisis = assess(f"{body.feelings}\n{body.direction}")["level"] == "crisis"

    row = MonthlyReflection(user_id=user.id, period=period, feelings=body.feelings, direction=body.direction)
    db.add(row)
    audit(db, user.id, "checkin.submitted", target=period)
    await db.commit()
    await db.refresh(row)
    entry = CheckinOut(
        id=str(row.id),
        period=row.period,
        feelings=row.feelings,
        direction=row.direction,
        created_at=row.created_at,
    )
    return CheckinResult(
        entry=entry,
        requires_human=crisis,
        contacts=CRISIS_CONTACTS if crisis else [],
    )
