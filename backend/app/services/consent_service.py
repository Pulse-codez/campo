"""Consent records: append-only, versioned, revocable (spec Section 11)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consent import ConsentRecord


async def record_consent(
    db: AsyncSession, user_id: uuid.UUID, scope: str, granted: bool, policy_version: str
) -> None:
    db.add(
        ConsentRecord(
            user_id=user_id,
            scope=scope,
            granted=granted,
            policy_version=policy_version,
        )
    )


async def latest_consents(db: AsyncSession, user_id: uuid.UUID) -> dict[str, ConsentRecord]:
    result = await db.execute(
        select(ConsentRecord)
        .where(ConsentRecord.user_id == user_id)
        .order_by(ConsentRecord.created_at.asc())
    )
    latest: dict[str, ConsentRecord] = {}
    for record in result.scalars():
        latest[record.scope] = record
    return latest


async def has_consent(db: AsyncSession, user_id: uuid.UUID, scope: str) -> bool:
    record = (await latest_consents(db, user_id)).get(scope)
    return bool(record and record.granted)
