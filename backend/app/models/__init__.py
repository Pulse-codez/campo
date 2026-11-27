"""SQLAlchemy models. Importing this package registers every table on Base.metadata."""

from app.models.audit_log import AuditLog
from app.models.base import Base, TimestampedModel
from app.models.consent import ConsentRecord
from app.models.conversation import Conversation
from app.models.counselling_session import CounsellingSession
<<<<<<< Updated upstream
from app.models.knowledge import KnowledgeChunk
from app.models.message import Message
from app.models.peer_match import PeerMatch
=======
from app.models.kind_note import KindNote
from app.models.message import Message
from app.models.reflection import MonthlyReflection
>>>>>>> Stashed changes
from app.models.university import University
from app.models.user import User

__all__ = [
    "AuditLog",
    "Base",
    "ConsentRecord",
    "Conversation",
    "CounsellingSession",
<<<<<<< Updated upstream
    "KnowledgeChunk",
    "Message",
    "PeerMatch",
=======
    "KindNote",
    "Message",
    "MonthlyReflection",
>>>>>>> Stashed changes
    "TimestampedModel",
    "University",
    "User",
]
