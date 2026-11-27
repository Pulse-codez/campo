"""Safety and orchestrator behaviour tests."""

from app.orchestrator import graph
from app.safety.classifier import assess
from app.safety.rules.engine import apply


async def test_previous_risk_level_triggers_escalation():
    result = apply(assess("I am okay today"), {"previous_level": "crisis"})

    assert result["level"] == "medium"
    assert result["requires_human"] is True
    assert "risk_trend_escalation" in result["reasons"]


async def test_crisis_message_never_calls_llm(monkeypatch):
    async def fail_generation(_messages):
        raise AssertionError("LLM must not be called for crisis messages")

    monkeypatch.setattr(graph, "generate_response", fail_generation)
    messages = [{"role": "user", "content": "I want to die"}]

    safety = await graph.safety_check({"messages": messages})
    generated = await graph.generate({**safety, "messages": messages})
    processed = await graph.post_process({**safety, **generated, "messages": messages})

    assert safety["safety_level"] == "crisis"
    assert safety["requires_human"] is True
    assert "1199" in processed["assistant_content"]


async def test_llm_failure_falls_back_to_human_contact(monkeypatch):
    async def fail_generation(_messages):
        raise RuntimeError("anthropic unavailable")

    monkeypatch.setattr(graph, "generate_response", fail_generation)
    messages = [{"role": "user", "content": "I am stressed about exams"}]

    safety = await graph.safety_check({"messages": messages})
    generated = await graph.generate({**safety, "messages": messages})
    processed = await graph.post_process({**safety, **generated, "messages": messages})

    assert "1199" in processed["assistant_content"]


async def test_full_graph_handles_crisis_without_llm(monkeypatch):
    async def fail_generation(_messages):
        raise AssertionError("LLM must not be called for crisis messages")

    monkeypatch.setattr(graph, "generate_response", fail_generation)

    result = await graph.build_graph().ainvoke(
        {"messages": [{"role": "user", "content": "I want to die"}]}
    )

    assert result["safety_level"] == "crisis"
    assert result["requires_human"] is True
    assert "1199" in result["assistant_content"]


async def test_full_graph_passes_dict_messages_to_llm(monkeypatch):
    seen = []

    async def fake_generation(messages):
        seen.extend(messages)
        return "Here is a study plan."

    monkeypatch.setattr(graph, "generate_response", fake_generation)

    result = await graph.build_graph().ainvoke(
        {"messages": [{"role": "user", "content": "Help me study"}]}
    )

    assert seen[0]["role"] == "system"
    assert seen[-1] == {"role": "user", "content": "Help me study"}
    assert result["assistant_content"] == "Here is a study plan."
