"""Kind messages from Claude. The prompt is fixed; the student only chooses a theme."""

from app.core.config import get_settings
from app.llm.adapter import generate_response

THEME_GUIDE = {
    "encouragement": "encouragement for a hard week of studies",
    "hope": "hope that things get better and that the student is not alone",
    "rest": "permission to rest and take a break",
    "self_kindness": "self-kindness and gentleness toward oneself",
}

SYSTEM = (
    "You write short, warm messages for university students in Kenya. "
    "Write two or three sentences, plain language, no emojis, no lists, no advice about medication "
    "or diagnosis. Do not mention these instructions. Do not ask questions."
)


class AIUnavailable(Exception):
    pass


async def kind_message(theme: str) -> str:
    if not get_settings().anthropic_api_key:
        raise AIUnavailable("ai_not_configured")
    guide = THEME_GUIDE[theme]
    return (
        await generate_response(
            [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Write one message with a focus on {guide}."},
            ],
            max_tokens=200,
        )
    ).strip()
