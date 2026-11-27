"""Safety check endpoint."""

from fastapi import APIRouter

from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.schemas.safety import SafetyAssessment, SafetyCheckRequest

router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("/check", response_model=SafetyAssessment)
async def safety_check(request: SafetyCheckRequest) -> SafetyAssessment:
    classified = classify(request.text)
    applied = apply_rules(classified, {})
    return SafetyAssessment(
        level=applied["level"],
        requires_human=applied["requires_human"],
        reasons=applied["reasons"],
        crisis_contacts=applied["crisis_contacts"],
    )
