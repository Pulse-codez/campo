"""Text-to-speech endpoint. Speech-to-text runs inside the conversation voice endpoint."""

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.api.deps import VoiceUser
from app.schemas.speech import TTSRequest
from app.services import speech_service
from app.services.speech_service import SpeechUnavailable

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/tts", response_class=Response)
async def text_to_speech(body: TTSRequest, user: VoiceUser):
    try:
        audio = await speech_service.synthesize(
            body.text,
            crisis=body.crisis,
            voice_preference=body.voice_preference or user.voice_preference,
            gender=user.gender,
        )
    except SpeechUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="speech_provider_error") from exc
    return Response(content=audio, media_type="audio/mpeg")
