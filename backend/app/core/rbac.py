"""Central role-based access policy.

Roles come from the JWT `sub`'s user row. Anonymous actors get only the
pseudo-role `anonymous`; they never access staff, admin or counselling data.
"""

from typing import Literal

Role = Literal["student", "peer_counsellor", "counsellor", "admin", "anonymous"]

PERMISSIONS: dict[str, frozenset[str]] = {
    "anonymous": frozenset({"chat:use", "peer:match", "mcp:use", "safety:check"}),
    "student": frozenset(
        {
            "chat:use",
            "peer:match",
            "mcp:use",
            "safety:check",
            "consent:manage",
            "counselling:request",
            "voice:use",
        }
    ),
    "peer_counsellor": frozenset(
        {"chat:use", "mcp:use", "safety:check", "voice:use", "counselling:view", "counselling:manage"}
    ),
    "counsellor": frozenset(
        {"chat:use", "mcp:use", "safety:check", "voice:use", "counselling:view", "counselling:manage"}
    ),
    "admin": frozenset(
        {
            "chat:use",
            "peer:match",
            "mcp:use",
            "safety:check",
            "consent:manage",
            "counselling:request",
            "counselling:view",
            "counselling:manage",
            "voice:use",
            "admin:manage",
            "knowledge:manage",
        }
    ),
}


def can(role: str, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, frozenset())
