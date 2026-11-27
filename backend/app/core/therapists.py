"""Concerns students can select at onboarding, and the virtual therapist recommended for each.

Virtual therapists are AI companions, not licensed clinicians. Every persona runs under the
same safety pipeline and system prompt as the base companion.
"""

from dataclasses import dataclass

CONCERNS: dict[str, str] = {
    "family_issues": "Family issues",
    "stress": "Stress",
    "peer_pressure": "Peer pressure",
    "suicide": "Suicide",
    "other": "Other",
}

# Highest priority first. Safety outranks everything else.
PRIORITY = ["suicide", "family_issues", "peer_pressure", "stress", "other"]


@dataclass(frozen=True)
class VirtualTherapist:
    key: str
    name: str
    focus: str
    persona: str
    concerns: tuple[str, ...]


THERAPISTS: dict[str, VirtualTherapist] = {
    "steady": VirtualTherapist(
        key="steady",
        name="Steady",
        focus="Safety first. Support when thoughts of suicide or self-harm come up.",
        persona=(
            "Focus: safety. Ask directly whether the student is safe right now. Encourage them to "
            "contact a person straight away (helpline, campus counsellor, or emergency services). "
            "Never explore methods. Keep replies short and calm."
        ),
        concerns=("suicide",),
    ),
    "bridge": VirtualTherapist(
        key="bridge",
        name="Bridge",
        focus="Family relationships, boundaries, and hard conversations at home.",
        persona=(
            "Focus: family relationships. Help the student name their feelings, set boundaries, and "
            "plan difficult conversations with family. Ask one gentle question at a time."
        ),
        concerns=("family_issues",),
    ),
    "anchor": VirtualTherapist(
        key="anchor",
        name="Anchor",
        focus="Peer pressure, self-worth, and learning to say no.",
        persona=(
            "Focus: peer pressure. Help the student notice what they want versus what their peers "
            "expect, practise saying no, and rebuild confidence in their own choices."
        ),
        concerns=("peer_pressure",),
    ),
    "calm": VirtualTherapist(
        key="calm",
        name="Calm",
        focus="Stress, overwhelm, and study pressure, with practical coping tools.",
        persona=(
            "Focus: stress. Offer grounding exercises, break large problems into small steps, and "
            "help the student plan rest. Keep suggestions practical and brief."
        ),
        concerns=("stress",),
    ),
    "open": VirtualTherapist(
        key="open",
        name="Open",
        focus="A general listening space for anything else on your mind.",
        persona=(
            "Focus: open listening. Reflect back what the student shares, ask what would help most, "
            "and gently point to campus services when needed."
        ),
        concerns=("other",),
    ),
}

PERSONA_DISCLOSURE = (
    "You are a virtual therapist for this student, an AI companion and not a licensed clinician. "
    "If asked, say so plainly."
)


def normalise_concerns(keys: list[str]) -> list[str]:
    seen: list[str] = []
    for key in keys:
        if key in CONCERNS and key not in seen:
            seen.append(key)
    return seen


def recommend(concerns: list[str]) -> VirtualTherapist:
    selected = normalise_concerns(concerns)
    for key in PRIORITY:
        if key in selected:
            return THERAPISTS[_therapist_for(key)]
    return THERAPISTS["open"]


def alternatives(concerns: list[str], primary: VirtualTherapist) -> list[VirtualTherapist]:
    return [t for t in THERAPISTS.values() if t.key != primary.key and set(t.concerns) & set(concerns)]


def persona_prompt(therapist_key: str | None) -> str:
    therapist = THERAPISTS.get(therapist_key or "")
    if therapist is None:
        return ""
    return f"{PERSONA_DISCLOSURE}\n{therapist.persona}"


def _therapist_for(concern: str) -> str:
    for therapist in THERAPISTS.values():
        if concern in therapist.concerns:
            return therapist.key
    return "open"
