"""One conversation turn: safety classification, orchestrator, persistence.

Both text and voice endpoints call run_turn, so the safety path is identical.
MCP supplies current context and escalation references; crisis never depends on
Claude or on MCP availability.
"""

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.orchestrator.graph import build_graph
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.schemas.conversation import (
    ChatResponse,
    ConversationCreate,
)
from app.services.audit_service import audit
from app.services.conversation_service import (
    add_message,
    build_history,
    create_conversation,
    get_conversation,
    get_messages,
)
from app.services.mcp_client import MCPClient

logger = logging.getLogger(__name__)

_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def _escalation_ticket(reason: str, urgency: str) -> str | None:
    """Ask the MCP tool server for a reference; never block safety on it."""
    try:
        result = await MCPClient().call_tool(
            "request_escalation", {"reason": reason, "urgency": urgency}
        )
    except Exception:
        logger.warning("MCP escalation unavailable", exc_info=True)
        return None
    ticket = getattr(result, "ticket_id", None)
    if ticket is None and isinstance(result, dict):
        ticket = result.get("ticket_id")
    return ticket


async def run_turn(
    db: AsyncSession,
    user: User | None,
    conversation_id: str | None,
    text: str,
    anonymous_token: str | None = None,
    mode: str = "ai",
) -> ChatResponse:
    if conversation_id is None:
        conv_out = await create_conversation(
            db,
            user.id if user else None,
            ConversationCreate(title=None, mode=mode),
            anonymous_token=anonymous_token,
        )
        conversation_id = conv_out.id

    conv = await get_conversation(db, user.id if user else None, conversation_id, anonymous_token)
    if conv is None:
        raise LookupError("conversation_not_found")

    # Classify once, with conversation context, before persisting the turn.
    prior = await get_messages(db, conv.id, limit=50)
    previous_level = next(
        (message.risk_level for message in reversed(prior) if message.risk_level), None
    )
    applied = apply_rules(classify(text), {"previous_level": previous_level})
    history = build_history(prior, text)

    user_msg = await add_message(db, conv.id, "user", text, applied["level"])

    result = await _get_graph().ainvoke(
        {
            "messages": history,
            "user_id": str(user.id) if user else "anonymous",
            "university_id": str(user.university_id) if user else None,
            "conversation_id": str(conv.id),
            "assessment": applied,
            "previous_level": previous_level,
        }
    )

    safety_level = result.get("safety_level", applied["level"])
    requires_human = bool(result.get("requires_human", applied["requires_human"]))
    assistant_content = result.get("assistant_content", "")

    ticket_id = None
    if requires_human:
        urgency = "crisis" if safety_level == "crisis" else "urgent"
        ticket_id = await _escalation_ticket(f"{safety_level}: {text[:500]}", urgency)
        audit(
            db,
            user.id if user else None,
            "safety.human_review_required",
            target=conv.public_id,
            details=json.dumps(
                {
                    "risk_level": safety_level,
                    "reasons": result.get("safety_reasons", applied.get("reasons", [])),
                    "user_message_id": user_msg.id,
                    "ticket_id": ticket_id,
                },
                sort_keys=True,
            ),
        )
        await db.commit()

    assistant_msg = await add_message(db, conv.id, "assistant", assistant_content, safety_level)

    return ChatResponse(
        conversation_id=conv.public_id,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
        assistant_content=assistant_content,
        risk_level=safety_level,
        requires_human=requires_human,
        mode=conv.mode,
        crisis_contacts=result.get("crisis_contacts", []),
        safety_reasons=result.get("safety_reasons", []),
        ticket_id=ticket_id,
    )
