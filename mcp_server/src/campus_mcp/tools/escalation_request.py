"""escalation_request: route a student to human support when needed."""

import uuid
from typing import Literal

from pydantic import BaseModel, Field

from campus_mcp.safety import is_crisis

Urgency = Literal["routine", "urgent", "crisis"]
PreferredChannel = Literal[
    "counselling", "health_clinic", "peer_support", "security", "other"
]


class EscalationInput(BaseModel):
    reason: str = Field(..., min_length=1, max_length=5000)
    urgency: Urgency = Field("routine", description="routine | urgent | crisis")
    preferred_channel: PreferredChannel | None = Field(None)


class EscalationOutput(BaseModel):
    ticket_id: str
    status: str
    estimated_response: str
    contacts: list[str]
    instructions: list[str]
    is_crisis: bool


def request_escalation(
    reason: str,
    urgency: str = "routine",
    preferred_channel: str | None = None,
) -> EscalationOutput:
    """Create an escalation and return immediate actions.

    Crisis cases are never queued — they get direct emergency contacts. Ticket
    IDs are deterministic (uuid5) so retries do not generate new references.
    """
    params = EscalationInput(
        reason=reason, urgency=urgency, preferred_channel=preferred_channel
    )
    crisis_flag = params.urgency == "crisis" or is_crisis(params.reason)

    if crisis_flag:
        return EscalationOutput(
            ticket_id="CRISIS-IMMEDIATE",
            status="crisis",
            estimated_response="immediate",
            contacts=[
                "National mental health helpline: 1199 (24/7, free)",
                "Campus security: +254 700 000 999 (on campus, 24/7)",
                "Nearest hospital emergency department",
            ],
            instructions=[
                "Do not wait for a ticket response.",
                "Call 1199 or go to the nearest emergency department now.",
                "If you're on campus, call campus security at +254 700 000 999.",
            ],
            is_crisis=True,
        )

    ticket_uuid = uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"campo:escalation:{params.reason}|{params.urgency}|{params.preferred_channel}",
    )
    contacts = [
        "University Counselling Centre: +254 700 000 100",
        "Campus Health Clinic: +254 700 000 101",
    ]
    if params.preferred_channel == "peer_support":
        contacts.append("Peer Support Network: peersupport@university.ac.ke")
    if params.preferred_channel == "security":
        contacts.append("Campus Security: +254 700 000 999")

    return EscalationOutput(
        ticket_id=f"ESC-{str(ticket_uuid)[:8].upper()}",
        status="received",
        estimated_response="within 24 hours (routine) or 4 hours (urgent)",
        contacts=contacts,
        instructions=[
            "A counsellor will contact you using the details on file.",
            "Keep this ticket ID for reference.",
            "If your situation worsens, call 1199 immediately.",
        ],
        is_crisis=False,
    )
