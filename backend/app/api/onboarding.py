"""Onboarding and consent endpoints."""

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbSession
from app.core.therapists import CONCERNS, THERAPISTS, normalise_concerns, recommend
from app.models.consent import CONSENT_SCOPES
from app.schemas.auth import UserOut
from app.schemas.onboarding import ConsentIn, ConsentOut, OnboardingIn
from app.services.audit_service import audit
from app.services.consent_service import latest_consents, record_consent

router = APIRouter(tags=["onboarding"])


@router.post("/onboarding", response_model=UserOut)
async def complete_onboarding(body: OnboardingIn, db: DbSession, user: CurrentUser):
    unknown = set(body.consents) - set(CONSENT_SCOPES)
    if unknown:
        raise HTTPException(status_code=422, detail=f"unknown_scopes: {sorted(unknown)}")
    invalid_concerns = set(body.concerns) - set(CONCERNS)
    if invalid_concerns:
        raise HTTPException(status_code=422, detail=f"unknown_concerns: {sorted(invalid_concerns)}")
    concerns = normalise_concerns(body.concerns)
    if not concerns:
        raise HTTPException(status_code=422, detail="concerns_required")

    wants_contact = body.consents.get("emergency_contact", False)
    if wants_contact and not (body.emergency_contact_name and body.emergency_contact_phone):
        raise HTTPException(status_code=422, detail="emergency_contact_required")

    for scope in CONSENT_SCOPES:
        await record_consent(
            db, user.id, scope, bool(body.consents.get(scope, False)), body.policy_version
        )

    user.onboarded = True
    user.concerns = ",".join(concerns)
    chosen = body.therapist_key if body.therapist_key in THERAPISTS else recommend(concerns).key
    user.therapist_key = chosen
    user.emergency_contact_name = body.emergency_contact_name if wants_contact else None
    user.emergency_contact_phone = body.emergency_contact_phone if wants_contact else None

    audit(db, user.id, "onboarding.completed", target=str(user.id))
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/consents", response_model=ConsentOut, status_code=201)
async def update_consent(body: ConsentIn, db: DbSession, user: CurrentUser):
    if body.scope not in CONSENT_SCOPES:
        raise HTTPException(status_code=422, detail="unknown_scope")
    await record_consent(db, user.id, body.scope, body.granted, body.policy_version)
    audit(db, user.id, "consent.changed", target=body.scope, details=str(body.granted))
    await db.commit()
    latest = (await latest_consents(db, user.id))[body.scope]
    return ConsentOut.model_validate(latest)


@router.get("/consents/me", response_model=list[ConsentOut])
async def my_consents(db: DbSession, user: CurrentUser):
    latest = await latest_consents(db, user.id)
    return [ConsentOut.model_validate(latest[s]) for s in CONSENT_SCOPES if s in latest]
