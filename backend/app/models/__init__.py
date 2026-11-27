"""SQLAlchemy models. Importing this package registers every table on Base.metadata."""

from app.models.audit_log import AuditLog
from app.models.base import Base, TimestampedModel
from app.models.consent import ConsentRecord
from app.models.conversation import Conversation
from app.models.counselling_session import CounsellingSession
from app.models.knowledge import KnowledgeChunk
from app.models.message import Message
from app.models.peer_match import PeerMatch
from app.models.university import University
from app.models.user import User

__all__ = [
    "AuditLog",
    "Base",
    "ConsentRecord",
    "Conversation",
    "CounsellingSession",
    "KnowledgeChunk",
    "Message",
    "PeerMatch",
    "TimestampedModel",
    "University",
    "User",
]
