"""Shared crisis screening for MCP tools.

This is a conservative keyword screen, not a clinical assessment. Every tool
that can encounter crisis language uses the same rules so a student never gets
different safety behaviour depending on which tool they call.
"""

import re

CRISIS_PHRASES = (
    "suicide",
    "suicidal",
    "kill myself",
    "end it",
    "end it all",
    "end my life",
    "self harm",
    "self-harm",
    "hurt myself",
    "overdose",
    "jump off",
    "jumped off",
    "jumping off",
    "hanging",
    "hang myself",
    "hung myself",
    "want to die",
    "better off dead",
    "kujiua",  # Swahili: kill oneself
    "najitaka kufa",  # Swahili: I want to die
)

_PATTERNS = tuple(
    re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
    for phrase in CRISIS_PHRASES
)


def is_crisis(*texts: str | None) -> bool:
    """Return True when any supplied text contains crisis language."""
    combined = " ".join(text for text in texts if text)
    return any(pattern.search(combined) for pattern in _PATTERNS)
