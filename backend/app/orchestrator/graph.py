"""LangGraph state graph for the support conversation.

  safety_check --(crisis)--> crisis_response --+
               --(other)--> retrieve_context --> generate --+
                                                            +--> post_process --> END

Crisis messages never reach the model. MCP context is retrieved for every
non-crisis turn so Claude answers with current campus information for both
typed and ElevenLabs voice turns.
"""

import logging
from typing import Any
from uuid import UUID

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from app.llm.adapter import generate_response
from app.llm.system_prompt import SYSTEM_PROMPT
from app.orchestrator.protocol import CRISIS_PROTOCOL_MESSAGE
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.services import context_service

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I'm having trouble responding right now. If you need urgent help, call the "
    "national mental health helpline at 1199 or go to the nearest emergency department."
)


class State(TypedDict, total=False):
    messages: list[dict[str, Any]]
    user_id: str
    university_id: str | None
    conversation_id: str
    previous_level: str | None
    assessment: dict[str, Any] | None
    persona: str
    safety_level: str
    requires_human: bool
    safety_reasons: list[str]
    crisis_contacts: list[str]
    mcp_context: str
    assistant_content: str


async def safety_check(state: State) -> dict[str, Any]:
    assessment = state.get("assessment")
    if assessment is None:
        last_user = next(
            (m for m in reversed(state.get("messages", [])) if m.get("role") == "user"),
            None,
        )
        assessment = apply_rules(
            classify(last_user["content"] if last_user else ""),
            {"previous_level": state.get("previous_level")},
        )
    return {
        "safety_level": assessment["level"],
        "requires_human": assessment["requires_human"],
        "safety_reasons": assessment.get("reasons", []),
        "crisis_contacts": assessment.get("crisis_contacts", []),
    }


def route_after_safety(state: State) -> str:
    return "crisis_response" if state.get("safety_level") == "crisis" else "retrieve_context"


async def crisis_response(state: State) -> dict[str, Any]:
    return {"assistant_content": CRISIS_PROTOCOL_MESSAGE, "requires_human": True}


async def retrieve_context(state: State) -> dict[str, Any]:
    last_user = next(
        (m for m in reversed(state.get("messages", [])) if m.get("role") == "user"),
        None,
    )
    query = last_user["content"] if last_user else ""
    university_id = state.get("university_id")
    try:
        context = await context_service.gather_context(
            query,
            state.get("safety_level", "none"),
            UUID(university_id) if university_id else None,
        )
        return {"mcp_context": context.as_prompt_block()}
    except Exception:
        # MCP is an enrichment, never a hard dependency of a support reply.
        logger.exception("MCP context retrieval failed")
        return {"mcp_context": ""}


async def generate(state: State) -> dict[str, Any]:
    system = SYSTEM_PROMPT
    if state.get("persona"):
        system = f"{system}\n\n{state['persona']}"
    if state.get("mcp_context"):
        system = f"{system}\n\n{state['mcp_context']}"
    messages = [{"role": "system", "content": system}, *state.get("messages", [])]
    try:
        content = await generate_response(messages)
    except Exception:
        logger.exception("LLM generation failed")
        content = CRISIS_PROTOCOL_MESSAGE if state.get("requires_human") else FALLBACK_RESPONSE
    return {"assistant_content": content}


async def post_process(state: State) -> dict[str, Any]:
    content = state.get("assistant_content", "")
    contacts = state.get("crisis_contacts", [])
    if state.get("requires_human") and contacts:
        additions = [contact for contact in contacts if contact not in content]
        if additions:
            content = f"{content}\n\nHuman support: " + "; ".join(additions)
    return {"assistant_content": content}


def build_graph():
    builder = StateGraph(State)
    builder.add_node("safety_check", safety_check)
    builder.add_node("crisis_response", crisis_response)
    builder.add_node("retrieve_context", retrieve_context)
    builder.add_node("generate", generate)
    builder.add_node("post_process", post_process)

    builder.add_edge(START, "safety_check")
    builder.add_conditional_edges(
        "safety_check",
        route_after_safety,
        {"crisis_response": "crisis_response", "retrieve_context": "retrieve_context"},
    )
    builder.add_edge("crisis_response", "post_process")
    builder.add_edge("retrieve_context", "generate")
    builder.add_edge("generate", "post_process")
    builder.add_edge("post_process", END)
    return builder.compile()
