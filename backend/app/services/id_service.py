"""Resolve client-facing IDs (5-char short IDs, with UUID fallback for old rows)."""

import re
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

PUBLIC_ID_RE = re.compile(r"^[A-Z0-9]{5}$")


async def find_by_public_id(db: AsyncSession, model: Any, value: str) -> Any | None:
    """Find a row by its short ID; also accept a legacy UUID for smooth upgrades."""
    candidate = value.strip().upper()
    if PUBLIC_ID_RE.fullmatch(candidate):
        return await db.scalar(select(model).where(model.public_id == candidate))
    try:
        legacy_uuid = UUID(value.strip())
    except (ValueError, AttributeError):
        return None
    return await db.get(model, legacy_uuid)
