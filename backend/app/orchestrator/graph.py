"""LangGraph state graph for the support conversation.

Nodes:
  1. safety_check      - classify user message for risk
  2. retrieve_context  - load conversation history
  3. generate          - call Claude adapter
  4. post_process      - attach safety metadata and crisis contacts
"""

from typing import Annotated

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.llm.adapter import generate_response
from app.llm.system_prompt import SYSTEM_PROMPT
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules


class State(TypedDict, total=False):
    messages: Annotated[list[dict], add_messages]
    user_id: str
    conversation_id: str
    safety_level: str
    requires_human: bool
    safety_reasons: list[str]
    crisis_contacts: list[str]
    assistant_content: str


async def safety_check(state: State) -> State:
    last_user = next(
        (m for m in reversed(state["messages"]) if m["role"] == "user"),
        None,
    )
    text = last_user["content"] if last_user else ""
    classified = classify(text)
    applied = apply_rules(classified, {})
    return {
        "safety_level": applied["level"],
        "requires_human": applied["requires_human"],
        "safety_reasons": applied["reasons"],
        "crisis_contacts": applied["crisis_contacts"],
    }


async def retrieve_context(state: State) -> State:
    # Placeholder: history is already in state["messages"] from the caller.
    # In production, load prior messages from the DB here.
    return state


async def generate(state: State) -> State:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *state["messages"]]
    content = await generate_response(messages)
    return {"assistant_content": content}


async def post_process(state: State) -> State:
    return state


def build_graph():
    builder = StateGraph(State)
    builder.add_node("safety_check", safety_check)
    builder.add_node("retrieve_context", retrieve_context)
    builder.add_node("generate", generate)
    builder.add_node("post_process", post_process)

    builder.add_edge(START, "safety_check")
    builder.add_edge("safety_check", "retrieve_context")
    builder.add_edge("retrieve_context", "generate")
    builder.add_edge("generate", "post_process")
    builder.add_edge("post_process", END)

    return builder.compile()
