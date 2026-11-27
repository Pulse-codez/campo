"""Safety rules: combines classifier output with conversation context."""

from typing import Any


def apply(classifier_result: dict, context: dict[str, Any] | None = None) -> dict:
    """Apply rules on top of the classifier result.

    context may include previous risk levels, user history, etc.
    Returns the final assessment dict.
    """
    level = classifier_result["level"]
    requires_human = classifier_result["requires_human"]
    reasons = list(classifier_result.get("reasons", []))
    contacts = list(classifier_result.get("crisis_contacts", []))

    # Escalate if the conversation has trended upward in risk
    if context:
        prev = context.get("previous_level")
        if prev in ("high", "crisis") and level in ("none", "low"):
            level = "medium"
            requires_human = True
            reasons.append("risk_trend_escalation")

    return {
        "level": level,
        "requires_human": requires_human,
        "reasons": reasons,
        "crisis_contacts": contacts,
    }
