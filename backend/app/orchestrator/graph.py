"""LangGraph state graph for the support conversation.

  safety_check --(crisis)--> crisis_response --> END        (no LLM)
               --(other)---> retrieve_context --> generate --> post_process --> END
"""

from typing import Any

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from app.llm.adapter import generate_response
from app.llm.system_prompt import SYSTEM_PROMPT
from app.orchestrator.protocol import CRISIS_PROTOCOL_MESSAGE
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules


class State(TypedDict, total=False):
    messages: list[dict[str, Any]]
    user_id: str
    conversation_id: str
    persona: str
    safety_level: str
    requires_human: bool
    safety_reasons: list[str]
    crisis_contacts: list[str]
    assistant_content: str


async def safety_check(state: State) -> dict[str, Any]:
    last_user = next((m for m in reversed(state["messages"]) if m["role"] == "user"), None)
    text = last_user["content"] if last_user else ""
    applied = apply_rules(classify(text), {})
    return {
        "safety_level": applied["level"],
        "requires_human": applied["requires_human"],
        "safety_reasons": applied["reasons"],
        "crisis_contacts": applied["crisis_contacts"],
    }


def route_after_safety(state: State) -> str:
    return "crisis_response" if state.get("safety_level") == "crisis" else "generate"


async def crisis_response(state: State) -> dict[str, Any]:
    return {"assistant_content": CRISIS_PROTOCOL_MESSAGE, "requires_human": True}


async def generate(state: State) -> dict[str, Any]:
    system = SYSTEM_PROMPT + (f"\n\n{state['persona']}" if state.get("persona") else "")
    messages = [{"role": "system", "content": system}, *state["messages"]]
    return {"assistant_content": await generate_response(messages)}


def build_graph():
    builder = StateGraph(State)
    builder.add_node("safety_check", safety_check)
    builder.add_node("crisis_response", crisis_response)
    builder.add_node("generate", generate)

    builder.add_edge(START, "safety_check")
    builder.add_conditional_edges(
        "safety_check",
        route_after_safety,
        {"crisis_response": "crisis_response", "generate": "generate"},
    )
    builder.add_edge("crisis_response", END)
    builder.add_edge("generate", END)
    return builder.compile()
