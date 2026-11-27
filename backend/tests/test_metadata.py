"""Tests for the shared SQLAlchemy metadata and API schemas."""

from datetime import UTC, datetime

from app.models import AuditLog, Conversation, Message, User
from app.models.base import Base, new_public_id
from app.schemas.auth import UserOut


def test_all_models_registered_on_shared_metadata():
    assert {"users", "conversations", "messages", "audit_logs"} <= set(Base.metadata.tables)
    assert AuditLog.__table__.metadata is Base.metadata
    assert Conversation.__table__.metadata is Base.metadata
    assert Message.__table__.metadata is Base.metadata
    assert User.__table__.metadata is Base.metadata


def test_user_out_exposes_short_public_id():
    short_id = new_public_id()
    user = UserOut(
        id=short_id,
        email="student@example.com",
        full_name=None,
        role="student",
        university_id=new_public_id(),
        onboarded=False,
        is_active=True,
        is_verified=False,
        created_at=datetime.now(UTC),
    )

    assert len(user.id) == 5 and user.id.isupper() and user.id.isalnum()
    assert user.gender is None and user.voice_preference == "auto"
