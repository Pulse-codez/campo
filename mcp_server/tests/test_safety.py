"""Shared crisis screening tests."""

import pytest

from campus_mcp.safety import is_crisis


@pytest.mark.parametrize(
    "text",
    [
        "I am thinking about suicide",
        "I want to kill myself",
        "I might self-harm tonight",
        "I want to hang myself",
        "I jumped off the bridge",
    ],
)
def test_detects_crisis_language(text: str):
    assert is_crisis(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "I have a heavy course load this semester",
        "I am worried about my exams",
        "I need help finding a counsellor",
        None,
    ],
)
def test_does_not_flag_ordinary_support_requests(text: str | None):
    assert is_crisis(text) is False
