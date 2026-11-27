"""Conversation history helper tests."""

from datetime import UTC, datetime

from app.schemas.conversation import MessageOut
from app.services.conversation_service import build_history


def test_build_history_appends_current_message_once():
    prior = [
        MessageOut(
            id="A1B2C",
            role="user",
            content="earlier question",
            risk_level="none",
            created_at=datetime.now(UTC),
        )
    ]

    history = build_history(prior, "new question")

    assert history == [
        {"role": "user", "content": "earlier question"},
        {"role": "user", "content": "new question"},
    ]
