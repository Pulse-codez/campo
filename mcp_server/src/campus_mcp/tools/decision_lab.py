"""decision_lab: structured decision support for health and wellbeing choices."""


from pydantic import BaseModel, Field


class Option(BaseModel):
    id: str
    label: str
    pros: list[str]
    cons: list[str]
    estimated_effort: str | None = None
    estimated_cost: str | None = None


class DecisionLabInput(BaseModel):
    situation: str = Field(..., description="The decision the student is facing")
    options: list[Option] = Field(..., min_items=2, description="Options to compare")
    values: list[str] = Field(
        ...,
        description="What matters most to the student, e.g. privacy, speed, cost, confidentiality",
    )


class DecisionLabOutput(BaseModel):
    recommended: str | None = None
    reasoning: str
    next_steps: list[str]
    crisis_flag: bool = False


def evaluate_decision(
    situation: str,
    options: list[Option],
    values: list[str],
) -> DecisionLabOutput:
    """Help a student weigh options using a simple values-aligned framework.

    This is decision support, not medical advice. It never makes the choice for
    the student and flags anything that sounds like a crisis for human review.
    """
    crisis_keywords = [
        "suicide", "kill myself", "end it", "self harm", "hurt myself",
        "overdose", "jump", "hanging",
    ]
    text = (situation + " " + " ".join(o.label + " " + " ".join(o.pros + o.cons) for o in options)).lower()
    crisis_flag = any(k in text for k in crisis_keywords)

    if crisis_flag:
        return DecisionLabOutput(
            recommended=None,
            reasoning=(
                "This sounds like it could involve safety concerns. I can't weigh "
                "options for this situation. Please reach a human right now."
            ),
            next_steps=[
                "Call the national mental health helpline at 1199 (24/7, free).",
                "Contact campus security at +254 700 000 999 if you're on campus.",
                "Go to the nearest hospital emergency department.",
            ],
            crisis_flag=True,
        )

    scored = []
    for option in options:
        score = 0
        option_text = (option.label + " " + " ".join(option.pros + option.cons)).lower()
        for v in values:
            if v.lower() in option_text:
                score += 1
        scored.append((score, option))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0][1] if scored else None

    reasoning = (
        f"Weighed {len(options)} options against what matters to you: "
        f"{', '.join(values)}. "
    )
    if top:
        reasoning += (
            f"'{top.label}' aligns most closely with your stated values. "
            "This is a suggestion, not a directive. You choose."
        )

    next_steps = [
        "Write down your top choice and one first step.",
        "If you're unsure, talk it through with a counsellor or trusted person.",
        "Revisit the decision in a few days, since needs can change.",
    ]

    return DecisionLabOutput(
        recommended=top.label if top else None,
        reasoning=reasoning,
        next_steps=next_steps,
        crisis_flag=False,
    )
