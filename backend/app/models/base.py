"""Declarative base, common columns and short public IDs."""

import secrets
import string
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

PUBLIC_ID_ALPHABET = string.ascii_uppercase + string.digits
PUBLIC_ID_LENGTH = 5


def new_public_id() -> str:
    """A 5-character uppercase alphanumeric ID, e.g. `K7Q2M`."""
    return "".join(secrets.choice(PUBLIC_ID_ALPHABET) for _ in range(PUBLIC_ID_LENGTH))


class Base(DeclarativeBase):
    pass


class TimestampedModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ShortIdModel(TimestampedModel):
    """Models exposed to clients also carry a collision-resistant short ID.

    The UUID primary key stays internal; APIs exchange only `public_id`.
    """

    __abstract__ = True

    public_id: Mapped[str] = mapped_column(
        String(PUBLIC_ID_LENGTH),
        unique=True,
        index=True,
        default=new_public_id,
    )
