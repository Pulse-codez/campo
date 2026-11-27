"""Safety check endpoint."""

from fastapi import APIRouter

from app.api.deps import SafetyActor
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.schemas.safety import SafetyAssessment, SafetyCheckRequest

router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("/check", response_model=SafetyAssessment)
async def safety_check(request: SafetyCheckRequest, _actor: SafetyActor) -> SafetyAssessment:
    classified = classify(request.text)
    applied = apply_rules(classified, {"previous_level": request.previous_level})
    return SafetyAssessment(
        level=applied["level"],
        requires_human=applied["requires_human"],
        reasons=applied["reasons"],
        crisis_contacts=applied["crisis_contacts"],
    )
