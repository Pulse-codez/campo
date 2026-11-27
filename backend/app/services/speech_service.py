"""ElevenLabs speech-to-text and text-to-speech. The only module that talks to ElevenLabs."""

import httpx

from app.core.config import get_settings

API_BASE = "https://api.elevenlabs.io/v1"


class SpeechUnavailable(Exception):
    pass


def _headers() -> dict[str, str]:
    key = get_settings().elevenlabs_api_key
    if not key:
        raise SpeechUnavailable("elevenlabs_not_configured")
    return {"xi-api-key": key}


async def transcribe(audio: bytes, filename: str, content_type: str) -> str:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE}/speech-to-text",
            headers=_headers(),
            data={"model_id": settings.elevenlabs_stt_model},
            files={"file": (filename, audio, content_type)},
        )
        resp.raise_for_status()
        return resp.json().get("text", "")


async def synthesize(text: str, crisis: bool = False) -> bytes:
    settings = get_settings()
    voice_id = settings.elevenlabs_crisis_voice_id if crisis else settings.elevenlabs_voice_id
    if not voice_id:
        raise SpeechUnavailable("elevenlabs_voice_not_configured")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE}/text-to-speech/{voice_id}",
            headers={**_headers(), "Accept": "audio/mpeg"},
            params={"output_format": "mp3_44100_128"},
            json={"text": text, "model_id": settings.elevenlabs_tts_model},
        )
        resp.raise_for_status()
        return resp.content
