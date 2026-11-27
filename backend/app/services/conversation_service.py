"""Conversation and message service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationOut, MessageOut


async def create_conversation(db: AsyncSession, user_id: UUID, data: ConversationCreate) -> ConversationOut:
    conv = Conversation(user_id=user_id, title=data.title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationOut.model_validate(conv)


async def list_conversations(db: AsyncSession, user_id: UUID) -> list[ConversationOut]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id, Conversation.is_archived == False)
        .order_by(Conversation.updated_at.desc())
    )
    return [ConversationOut.model_validate(c) for c in result.scalars().all()]


async def get_conversation(db: AsyncSession, user_id: UUID, conversation_id: UUID) -> Conversation | None:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_messages(db: AsyncSession, conversation_id: UUID, limit: int = 50) -> list[MessageOut]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    # Return oldest-first
    return [MessageOut.model_validate(m) for m in reversed(messages)]


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
        content=content,
        risk_level=risk_level,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return MessageOut.model_validate(msg)
