"""Bridge between MCP tools and Claude's conversation context.

Claude is the component that holds the conversation context for voice and text
turns. This service asks the MCP server for current, structured support context
(policies and resources) and injects it into Claude's system context each turn,
so the same facts are available whether the student typed or spoke.
"""

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.services import knowledge_service
from app.services.mcp_client import MCPClient

logger = logging.getLogger(__name__)


@dataclass
class SupportContext:
    policies: list[Any] = field(default_factory=list)
    resources: list[Any] = field(default_factory=list)
    knowledge: list[Any] = field(default_factory=list)
    tool_errors: list[str] = field(default_factory=list)

    def as_prompt_block(self) -> str:
        if not self.policies and not self.resources and not self.knowledge:
            return ""
        lines = ["CURRENT SUPPORT CONTEXT (from campus MCP tools; prefer these over guesses):"]
        for policy in self.policies:
            title = getattr(policy, "title", str(policy))
            summary = getattr(policy, "summary", "")
            contact = getattr(policy, "contact_email", None)
            lines.append(f"- Policy: {title}. {summary}" + (f" Contact: {contact}" if contact else ""))
        for resource in self.resources:
            name = getattr(resource, "name", str(resource))
            contact = getattr(resource, "contact", "")
            hours = getattr(resource, "hours", "")
            lines.append(f"- Resource: {name}. Contact: {contact}. Hours: {hours}.")
        for item in self.knowledge:
            title = getattr(item, "title", str(item))
            source = getattr(item, "source", None)
            excerpt = getattr(item, "excerpt", "")
            lines.append(f"- Campus knowledge: {title}. {excerpt}" + (f" (source: {source})" if source else ""))
        lines.append("Never present these as clinical advice; point to humans for safety.")
        return "\n".join(lines)


def _field(item: Any, name: str) -> str:
    if isinstance(item, dict):
        return str(item.get(name, ""))
    return str(getattr(item, name, "") or "")


async def gather_context(
    query: str,
    risk_level: str = "none",
    university_id: UUID | None = None,
) -> SupportContext:
    """Fetch relevant policies, resources and vector knowledge; degrade gracefully."""
    context = SupportContext()
    client = MCPClient()
    truncated = query.strip()[:120] or "student wellbeing support"

    resource_type = "counselling"
    lowered = query.lower()
    if any(
        word in lowered
        for word in (
            "hostel",
            "housing",
            "accommodation",
            "rent",
            "money",
            "fees",
            "bursary",
            "financial",
        )
    ):
        resource_type = "other"

    try:
        context.policies = await client.call_tool(
            "search_policies", {"query": truncated, "limit": 3}
        )
    except Exception as exc:  # noqa: BLE001 - MCP is an optional enrichment
        context.tool_errors.append(f"search_policies: {type(exc).__name__}")
        logger.warning("MCP policy lookup failed: %s", exc)

    try:
        context.resources = await client.call_tool(
            "find_resources", {"resource_type": resource_type}
        )
    except Exception as exc:  # noqa: BLE001 - MCP is an optional enrichment
        context.tool_errors.append(f"find_resources: {type(exc).__name__}")
        logger.warning("MCP resource lookup failed: %s", exc)

    if risk_level in ("high", "crisis"):
        try:
            emergency = await client.call_tool(
                "find_resources", {"resource_type": "emergency"}
            )
            context.resources.extend(emergency)
        except Exception as exc:  # noqa: BLE001 - MCP is an optional enrichment
            context.tool_errors.append(f"emergency resources: {type(exc).__name__}")
            logger.warning("MCP emergency lookup failed: %s", exc)

    try:
        async with AsyncSessionLocal() as db:
            context.knowledge = await knowledge_service.search(db, query, university_id)
    except Exception as exc:  # noqa: BLE001 - vector search is an optional enrichment
        context.tool_errors.append(f"knowledge_search: {type(exc).__name__}")
        logger.warning("Vector knowledge lookup failed: %s", exc)

    return context
