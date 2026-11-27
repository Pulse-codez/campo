"""Conversation endpoints: anonymous/registered, text turn, voice turn."""

from typing import Annotated

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import ChatActor, DbSession
from app.core.config import get_settings
from app.schemas.conversation import (
    AnonymousConversationCreate,
    AnonymousConversationOut,
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
    new_anonymous_token,
)
from app.services.speech_service import SpeechUnavailable

router = APIRouter(prefix="/conversations", tags=["conversations"])

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/mp4",
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/ogg",
    "audio/3gpp",
}


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conv(data: ConversationCreate, db: DbSession, actor: ChatActor):
    return await create_conversation(db, actor.id, data)


@router.post("/anonymous", response_model=AnonymousConversationOut, status_code=201)
async def create_anonymous_conv(data: AnonymousConversationCreate, db: DbSession):
    """Start an account-free chat; the token is returned once and proves ownership."""
    token = new_anonymous_token()
    out = await create_conversation(
        db,
        None,
        ConversationCreate(title=data.title),
        anonymous_token=token,
    )
    return AnonymousConversationOut(**out.model_dump(), anonymous_token=token)


@router.get("", response_model=list[ConversationOut])
async def list_convs(db: DbSession, actor: ChatActor):
    if actor.id is None:
        return []
    return await list_conversations(db, actor.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_conv_messages(conversation_id: str, db: DbSession, actor: ChatActor):
    conv = await get_conversation(db, actor.id, conversation_id, actor.anonymous_token)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation_not_found")
    return await get_messages(db, conv.id, limit=100)


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: DbSession, actor: ChatActor):
    try:
        return await run_turn(
            db,
            actor.user,
            body.conversation_id,
            body.message,
            anonymous_token=actor.anonymous_token,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{conversation_id}/voice", response_model=VoiceTurnResponse)
async def voice_turn(
    conversation_id: str,
    db: DbSession,
    actor: ChatActor,
    audio: Annotated[UploadFile, File(...)],
):
    """Transcribe with ElevenLabs, then run the same safety-first turn as text."""
    settings = get_settings()
    content_type = (audio.content_type or "").split(";", 1)[0].strip().lower()
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="unsupported_audio_type")

    payload = await audio.read(settings.max_audio_bytes + 1)
    if not payload:
        raise HTTPException(status_code=422, detail="empty_audio")
    if len(payload) > settings.max_audio_bytes:
        raise HTTPException(status_code=413, detail="audio_too_large")

    if await get_conversation(db, actor.id, conversation_id, actor.anonymous_token) is None:
        raise HTTPException(status_code=404, detail="conversation_not_found")

    try:
        transcript = await speech_service.transcribe(
            payload, audio.filename or "speech.webm", content_type
        )
    except SpeechUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="speech_provider_error") from exc

    transcript = transcript.strip()
    if not transcript:
        raise HTTPException(status_code=422, detail="empty_transcript")
    if len(transcript) > 10000:
        raise HTTPException(status_code=413, detail="transcript_too_long")

    try:
        turn = await run_turn(
            db,
            actor.user,
            conversation_id,
            transcript,
            anonymous_token=actor.anonymous_token,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return VoiceTurnResponse(transcript=transcript, turn=turn)
