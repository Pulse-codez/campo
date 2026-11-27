"""Claude conversation adapter.

Imports the Anthropic SDK only here so the rest of the app stays vendor-neutral.
"""

from anthropic import AsyncAnthropic

from app.core.config import get_settings

settings = get_settings()

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.llm_timeout_seconds,
        )
    return _client


async def generate_response(
    messages: list[dict],
    model: str | None = None,
    max_tokens: int = 1000,
) -> str:
    """Generate a Claude response from a list of {role, content} messages."""
    client = get_client()
    model = model or settings.anthropic_model

    system_messages = [m for m in messages if m["role"] == "system"]
    chat_messages = [m for m in messages if m["role"] in ("user", "assistant")]

    system_prompt = "\n".join(m["content"] for m in system_messages) or None

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=chat_messages,
    )

    # Concatenate text blocks
    return "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )
