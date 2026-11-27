"""One conversation turn: safety classification, orchestrator, persistence.

Both the text and voice endpoints call run_turn, so the safety path is the same for both.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.orchestrator.graph import build_graph
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.schemas.conversation import ChatResponse, ConversationCreate
from app.services.conversation_service import (
    add_message,
    create_conversation,
    get_conversation,
    get_messages,
)

_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def run_turn(
    db: AsyncSession,
    user: User,
    conversation_id: UUID | None,
    text: str,
) -> ChatResponse:
    if conversation_id is None:
        conv = await create_conversation(db, user.id, ConversationCreate(title=None))
        conversation_id = conv.id

    conv = await get_conversation(db, user.id, conversation_id)
    if conv is None:
        raise LookupError("conversation_not_found")

    applied = apply_rules(classify(text), {})
    user_msg = await add_message(db, conv.id, "user", text, applied["level"])

    # History includes the message just saved, so it is not appended again.
    history = [{"role": m.role, "content": m.content} for m in await get_messages(db, conv.id, limit=50)]

    result = await _get_graph().ainvoke(
        {
            "messages": history,
            "user_id": str(user.id),
            "conversation_id": str(conv.id),
        }
    )

    safety_level = result.get("safety_level", applied["level"])
    requires_human = result.get("requires_human", applied["requires_human"])
    assistant_content = result.get("assistant_content", "")

    assistant_msg = await add_message(db, conv.id, "assistant", assistant_content, safety_level)

    return ChatResponse(
        conversation_id=conv.id,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
        assistant_content=assistant_content,
        risk_level=safety_level,
        requires_human=requires_human,
    )
