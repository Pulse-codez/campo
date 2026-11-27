"""Conversation and message service. Message bodies are encrypted at rest."""

import hashlib
import secrets
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationOut, MessageOut
from app.services.crypto_service import decrypt, encrypt
from app.services.id_service import find_by_public_id


def new_anonymous_token() -> str:
    return secrets.token_urlsafe(32)


def hash_anonymous_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def build_history(prior: list[MessageOut], current_message: str) -> list[dict[str, str]]:
    """Build orchestrator messages from prior history plus the current prompt."""
    return [{"role": m.role, "content": m.content} for m in prior] + [
        {"role": "user", "content": current_message}
    ]


async def create_conversation(
    db: AsyncSession,
    user_id: UUID | None,
    data: ConversationCreate,
    anonymous_token: str | None = None,
) -> ConversationOut:
    conv = Conversation(
        user_id=user_id,
        title=data.title,
        mode=data.mode,
        anonymous_token_hash=hash_anonymous_token(anonymous_token) if anonymous_token else None,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationOut.from_conversation(conv)


async def list_conversations(db: AsyncSession, user_id: UUID) -> list[ConversationOut]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id, Conversation.is_archived.is_(False))
        .order_by(Conversation.updated_at.desc())
    )
    return [ConversationOut.from_conversation(c) for c in result.scalars().all()]


async def get_conversation(
    db: AsyncSession,
    user_id: UUID | None,
    conversation_id: str,
    anonymous_token: str | None = None,
) -> Conversation | None:
    """Look up by the 5-character public ID (legacy UUIDs still resolve)."""
    conv = await find_by_public_id(db, Conversation, conversation_id)
    if conv is None or conv.is_archived:
        return None
    if user_id is not None:
        return conv if conv.user_id == user_id else None
    if anonymous_token:
        return conv if conv.anonymous_token_hash == hash_anonymous_token(anonymous_token) else None
    return None


async def get_messages(db: AsyncSession, conversation_id: UUID, limit: int = 50) -> list[MessageOut]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    out = []
    for message in reversed(messages):
        out.append(MessageOut.from_message(message, decrypt(message.content)))
    return out


async def add_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    risk_level: str | None = None,
) -> MessageOut:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=encrypt(content),
        risk_level=risk_level,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return MessageOut.from_message(msg, content)
