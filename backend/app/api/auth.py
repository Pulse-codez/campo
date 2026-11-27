"""Auth endpoints: register (university-scoped), login, refresh, me."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import CurrentUser, DbSession
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
    VoicePreferenceIn,
)
from app.services import auth_service
from app.services.audit_service import audit

router = APIRouter(prefix="/auth", tags=["auth"])

bearer = HTTPBearer()

REGISTER_ERRORS = {
    "university_not_found": 422,
    "email_domain_not_allowed": 422,
    "email_already_registered": status.HTTP_409_CONFLICT,
    "other_university_name_required": 422,
    "other_email_not_accepted": 422,
}


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: DbSession):
    try:
        user = await auth_service.register_student(db, data)
    except ValueError as exc:
        code = str(exc)
        raise HTTPException(REGISTER_ERRORS.get(code, 400), detail=code) from exc
    return auth_service.tokens_for_user(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: DbSession):
    user = await auth_service.authenticate(db, data)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    audit(db, user.id, "auth.login")
    await db.commit()
    return auth_service.tokens_for_user(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: DbSession,
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="invalid_token")
    try:
        user_id = UUID(str(payload.get("sub")))
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid_token") from None
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="invalid_token")
    return auth_service.tokens_for_user(user)


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser):
    return UserOut.from_user(current_user)


@router.patch("/me/voice", response_model=UserOut)
async def set_voice_preference(body: VoicePreferenceIn, db: DbSession, current_user: CurrentUser):
    """Let students pick auto (opposite gender voice), male or female."""
    current_user.voice_preference = body.preference
    audit(db, current_user.id, "profile.voice_preference_changed", details=body.preference)
    await db.commit()
    await db.refresh(current_user)
    return UserOut.from_user(current_user)

