"""decision_lab: structured decision support for health and wellbeing choices."""

from pydantic import BaseModel, Field

from campus_mcp.safety import is_crisis


class Option(BaseModel):
    id: str
    label: str
    pros: list[str]
    cons: list[str]
    estimated_effort: str | None = None
    estimated_cost: str | None = None


class DecisionLabInput(BaseModel):
    situation: str = Field(..., min_length=1, max_length=5000)
    options: list[Option] = Field(..., min_length=2, max_length=10)
    values: list[str] = Field(..., min_length=1, max_length=10)


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
    """Weigh options against the student's values; flag crisis language first."""
    params = DecisionLabInput(situation=situation, options=options, values=values)
    option_text = [
        " ".join([option.label, *option.pros, *option.cons])
        for option in params.options
    ]
    if is_crisis(params.situation, *option_text):
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
    for option in params.options:
        score = 0
        candidate = " ".join([option.label, *option.pros, *option.cons]).lower()
        for value in params.values:
            if value.lower() in candidate:
                score += 1
        scored.append((score, option))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[0][1] if scored else None
    reasoning = (
        f"Weighed {len(params.options)} options against what matters to you: "
        f"{', '.join(params.values)}. "
    )
    if top:
        reasoning += (
            f"'{top.label}' aligns most closely with your stated values. "
            "This is a suggestion, not a directive. You choose."
        )


    return DecisionLabOutput(
        recommended=top.label if top else None,
        reasoning=reasoning,
        next_steps=[
            "Write down your top choice and one first step.",
            "If you're unsure, talk it through with a counsellor or trusted person.",
            "Revisit the decision in a few days — needs can change.",
        ],
        crisis_flag=False,
    )
