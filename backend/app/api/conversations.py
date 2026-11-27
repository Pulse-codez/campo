"""Conversation endpoints: list, history, text turn, and voice turn."""

from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import CurrentUser, DbSession
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationOut,
    MessageOut,
    VoiceTurnResponse,
)
from app.services import speech_service
from app.services.chat_service import run_turn
from app.services.conversation_service import (
    create_conversation,
    get_conversation,
    get_messages,
    list_conversations,
)
from app.services.speech_service import SpeechUnavailable

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conv(data: ConversationCreate, db: DbSession, user: CurrentUser):
    return await create_conversation(db, user.id, data)


@router.get("", response_model=list[ConversationOut])
async def list_convs(db: DbSession, user: CurrentUser):
    return await list_conversations(db, user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_conv_messages(conversation_id: UUID, db: DbSession, user: CurrentUser):
    if await get_conversation(db, user.id, conversation_id) is None:
        raise HTTPException(status_code=404, detail="conversation_not_found")
    return await get_messages(db, conversation_id)


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: DbSession, user: CurrentUser):
    try:
        return await run_turn(db, user, body.conversation_id, body.message)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{conversation_id}/voice", response_model=VoiceTurnResponse)
async def voice_turn(
    conversation_id: UUID,
    db: DbSession,
    user: CurrentUser,
    audio: Annotated[UploadFile, File()],
):
    """Transcribe the upload, then run the same safety-first turn as typed text.

    The raw audio is not stored; only the transcript goes into the conversation.
    """
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=422, detail="empty_audio")

    try:
        transcript = await speech_service.transcribe(
            data,
            audio.filename or "speech.webm",
            audio.content_type or "audio/webm",
        )
    except SpeechUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="speech_provider_error") from exc

    if not transcript.strip():
        raise HTTPException(status_code=422, detail="no_speech_detected")

    try:
        turn = await run_turn(db, user, conversation_id, transcript)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return VoiceTurnResponse(transcript=transcript, turn=turn)
