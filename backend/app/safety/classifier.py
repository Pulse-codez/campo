"""Rule-based crisis and risk text classifier.

This is a first-pass safety screen. It never replaces a human clinician.
"""

CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end it all",
    "end my life",
    "self harm",
    "self-harm",
    "hurt myself",
    "overdose",
    "jump off",
    "hanging",
    "want to die",
    "better off dead",
]

HIGH_KEYWORDS = [
    "panic attack",
    "can't breathe",
    "unable to cope",
    "giving up",
    "hopeless",
    "worthless",
    "burden",
    "cutting",
    "burning",
    "pills",
]


def assess(text: str) -> dict:
    """Return {level, requires_human, reasons, crisis_contacts} for the given text.

    Levels: none | low | medium | high | crisis
    """
    lowered = text.lower()
    reasons: list[str] = []

    if any(k in lowered for k in CRISIS_KEYWORDS):
        return {
            "level": "crisis",
            "requires_human": True,
            "reasons": ["crisis_keywords_detected"],
            "crisis_contacts": [
                "National mental health helpline: 1199 (24/7, free)",
                "Campus security: +254 700 000 999 (on campus, 24/7)",
                "Nearest hospital emergency department",
            ],
        }

    if any(k in lowered for k in HIGH_KEYWORDS):
        reasons.append("high_risk_keywords_detected")
        return {
            "level": "high",
            "requires_human": True,
            "reasons": reasons,
            "crisis_contacts": [
                "University Counselling Centre: +254 700 000 100",
                "National mental health helpline: 1199 (24/7, free)",
            ],
        }

    return {
        "level": "none",
        "requires_human": False,
        "reasons": [],
        "crisis_contacts": [],
    }
