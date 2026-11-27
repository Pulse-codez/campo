"""ElevenLabs speech-to-text and text-to-speech. The only module that talks to ElevenLabs."""

import httpx

from app.core.config import get_settings
from app.schemas.auth import VoicePreference

API_BASE = "https://api.elevenlabs.io/v1"


class SpeechUnavailable(Exception):
    pass


def _headers() -> dict[str, str]:
    key = get_settings().elevenlabs_api_key
    if not key:
        raise SpeechUnavailable("elevenlabs_not_configured")
    return {"xi-api-key": key}


def resolve_voice_id(
    preference: VoicePreference | str = "auto",
    gender: str | None = None,
    crisis: bool = False,
) -> str:
    """Pick a named voice. `auto` uses the opposite of the student's gender.

    Female students hear the male voice and male students hear the female voice
    by default; an explicit preference always wins. The crisis voice takes
    priority because it is deliberately calmer.
    """
    settings = get_settings()
    female = settings.elevenlabs_voice_id_female
    male = settings.elevenlabs_voice_id_male

    if crisis and settings.elevenlabs_crisis_voice_id:
        return settings.elevenlabs_crisis_voice_id

    if preference == "female":
        chosen = female
    elif preference == "male" or gender == "female":
        chosen = male
    elif gender == "male":
        chosen = female
    else:
        chosen = female or male

    return chosen or settings.elevenlabs_voice_id


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


async def synthesize(
    text: str,
    crisis: bool = False,
    voice_preference: VoicePreference | str = "auto",
    gender: str | None = None,
) -> bytes:
    voice_id = resolve_voice_id(voice_preference, gender, crisis)
    if not voice_id:
        raise SpeechUnavailable("elevenlabs_voice_not_configured")
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{API_BASE}/text-to-speech/{voice_id}",
            headers={**_headers(), "Accept": "audio/mpeg"},
            params={"output_format": "mp3_44100_128"},
            json={"text": text, "model_id": settings.elevenlabs_tts_model},
        )
        resp.raise_for_status()
        return resp.content
