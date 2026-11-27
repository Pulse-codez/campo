"""Audit events. Added to the session; the caller commits with the action it describes."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def audit(
    db: AsyncSession,
    user_id: uuid.UUID | None,
    action: str,
    target: str | None = None,
    details: str | None = None,
) -> None:
    db.add(AuditLog(user_id=user_id, action=action, target=target, details=details))
