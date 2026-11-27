"""In-memory tests for the registered FastMCP tools."""

import asyncio

from fastmcp import Client

from campus_mcp.server import mcp


def call_tool(name: str, arguments: dict):
    async def invoke():
        async with Client(mcp) as client:
            result = await client.call_tool(name, arguments)
            assert result.is_error is False
            return result.data

    return asyncio.run(invoke())


def test_policy_search_filters_and_limits():
    results = call_tool(
        "search_policies",
        {"query": "mental health", "category": "mental_health", "limit": 1},
    )

    assert len(results) == 1
    assert results[0].id == "pol-001"
    assert results[0].category == "mental_health"


def test_resource_finder_filters_by_type():
    results = call_tool(
        "find_resources",
        {"resource_type": "emergency", "hours": "24 hours"},
    )

    assert {result.id for result in results} == {"res-004", "res-005"}


def test_study_plan_total_matches_sessions():
    plan = call_tool(
        "plan_study",
        {
            "units": ["Biochemistry", "Chemistry"],
            "hours_per_week": 7,
            "energy_level": "low",
        },
    )

    session_minutes = sum(session.duration_minutes for session in plan.sessions)
    assert plan.total_hours == round(session_minutes / 60, 2)
    assert all(session.duration_minutes <= 120 for session in plan.sessions)
    assert plan.total_hours == 4.2


def test_decision_lab_flags_crisis_in_situation_or_options():
    options = [
        {
            "id": "a",
            "label": "Talk to someone",
            "pros": ["confidential"],
            "cons": ["takes time"],
        },
        {
            "id": "b",
            "label": "Wait it out",
            "pros": ["no effort"],
            "cons": ["I feel hopeless"],
        },
    ]

    result = call_tool(
        "evaluate_decision",
        {"situation": "I want to end it all", "options": options, "values": ["privacy"]},
    )
    assert result.crisis_flag is True
    assert result.recommended is None
    assert any("1199" in step for step in result.next_steps)


def test_escalation_ticket_is_deterministic():
    arguments = {"reason": "I need someone to talk to", "urgency": "routine"}

    first = call_tool("request_escalation", arguments)
    second = call_tool("request_escalation", arguments)

    assert first.ticket_id == second.ticket_id
    assert first.ticket_id.startswith("ESC-")
    assert first.is_crisis is False
