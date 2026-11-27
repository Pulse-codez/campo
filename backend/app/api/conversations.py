"""Conversation and chat endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.orchestrator.graph import build_graph
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationOut,
    MessageOut,
)
from app.services.conversation_service import (
    add_message,
    create_conversation,
    get_conversation,
    get_messages,
    list_conversations,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conv(
    data: ConversationCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_conversation(db, current_user.id, data)


@router.get("", response_model=list[ConversationOut])
async def list_convs(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await list_conversations(db, current_user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_conv_messages(
    conversation_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    conv = await get_conversation(db, current_user.id, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="conversation_not_found")
    return await get_messages(db, conversation_id)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    graph = build_graph()

    # Resolve or create conversation
    conversation_id = request.conversation_id
    if conversation_id is None:
        conv = await create_conversation(db, current_user.id, ConversationCreate(title=None))
        conversation_id = conv.id

    conv = await get_conversation(db, current_user.id, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="conversation_not_found")

    # Safety check on user message
    classified = classify(request.message)
    applied = apply_rules(classified, {})

    # Save user message
    user_msg = await add_message(
        db, conversation_id, "user", request.message, applied["level"]
    )

    # Build message history for the orchestrator
    prior = await get_messages(db, conversation_id, limit=50)
    history = [
        {"role": m.role, "content": m.content} for m in prior
    ]
    history.append({"role": "user", "content": request.message})

    # Run orchestrator
    result = await graph.ainvoke(
        {
            "messages": history,
            "user_id": str(current_user.id),
            "conversation_id": str(conversation_id),
        }
    )

    assistant_content = result.get("assistant_content", "")
    safety_level = result.get("safety_level", applied["level"])
    requires_human = result.get("requires_human", applied["requires_human"])

    assistant_msg = await add_message(
        db,
        conversation_id,
        "assistant",
        assistant_content,
        safety_level,
    )

    return ChatResponse(
        conversation_id=conversation_id,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
        assistant_content=assistant_content,
        risk_level=safety_level,
        requires_human=requires_human,
    )
