"""escalation_request — route a student to human support when needed."""


from pydantic import BaseModel, Field


class EscalationInput(BaseModel):
    reason: str = Field(..., description="Why the student needs human support")
    urgency: str = Field(
        "routine",
        description="Urgency level: routine, urgent, crisis",
    )
    preferred_channel: str | None = Field(
        None,
        description="Preferred channel: counselling, health_clinic, peer_support, security, other",
    )


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
    """Create an escalation to human support and return immediate actions.

    Placeholder implementation. Wire this to the university's ticketing or
    case-management system before production. Crisis cases are never queued —
    they are given direct emergency contacts.
    """
    crisis_keywords = ["suicide", "kill myself", "end it", "self harm", "hurt myself", "overdose"]
    is_crisis = urgency == "crisis" or any(k in reason.lower() for k in crisis_keywords)

    if is_crisis:
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

    contacts = [
        "University Counselling Centre: +254 700 000 100",
        "Campus Health Clinic: +254 700 000 101",
    ]
    if preferred_channel == "peer_support":
        contacts.append("Peer Support Network: peersupport@university.ac.ke")
    if preferred_channel == "security":
        contacts.append("Campus Security: +254 700 000 999")

    return EscalationOutput(
        ticket_id=f"ESC-{abs(hash(reason)) % 100000:05d}",
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
