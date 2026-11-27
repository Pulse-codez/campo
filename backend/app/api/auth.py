"""Auth endpoints: register, login, refresh, me."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserOut, UserRegister
from app.services.auth_service import authenticate, tokens_for_user
from app.services.auth_service import register as svc_register

router = APIRouter(prefix="/auth", tags=["auth"])

bearer = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        await svc_register(db, data)
    except ValueError as exc:
        if str(exc) == "email_already_registered":
            raise HTTPException(status_code=409, detail="email_already_registered") from exc
        raise

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one()
    return await tokens_for_user(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await authenticate(db, data)
    if not user:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    return await tokens_for_user(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="invalid_token")
    access = create_access_token(payload["sub"])
    refresh = create_refresh_token(payload["sub"])
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserOut)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
