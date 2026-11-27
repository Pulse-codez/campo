"""FastAPI dependencies: DB session, current user, RBAC and anonymous access."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.core.rbac import can
from app.core.security import decode_token
from app.models.user import User

bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid_credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden() -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient_role")


async def _user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None, db: AsyncSession
) -> User | None:
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise _invalid_credentials()
    try:
        uid = UUID(str(payload.get("sub")))
    except ValueError:
        raise _invalid_credentials() from None
    user = await db.scalar(
        select(User).where(User.id == uid).options(selectinload(User.university))
    )
    if user is None or not user.is_active:
        raise _invalid_credentials()
    return user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: DbSession,
) -> User:
    user = await _user_from_credentials(credentials, db)
    if user is None:
        raise _invalid_credentials()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@dataclass
class Actor:
    """Either a registered user or an anonymous session proven by a token."""

    user: User | None
    anonymous_token: str | None = None

    @property
    def id(self) -> UUID | None:
        return self.user.id if self.user else None

    @property
    def role(self) -> str:
        return self.user.role if self.user else "anonymous"


async def get_actor(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer)],
    db: DbSession,
    x_anonymous_token: Annotated[str | None, Header(alias="X-Anonymous-Token")] = None,
) -> Actor:
    user = await _user_from_credentials(credentials, db)
    if user is None and not x_anonymous_token:
        raise _invalid_credentials()
    return Actor(user=user, anonymous_token=x_anonymous_token)


ActorDep = Annotated[Actor, Depends(get_actor)]


def require_permission(permission: str):
    """RBAC for actors; anonymous sessions are allowed only if their role permits it."""

    async def checker(actor: ActorDep) -> Actor:
        if not can(actor.role, permission):
            raise _forbidden()
        return actor

    return checker


def require_user_permission(permission: str):
    """RBAC for endpoints that require a registered account."""

    async def checker(user: CurrentUser) -> User:
        if not can(user.role, permission):
            raise _forbidden()
        return user

    return checker


StaffUser = Annotated[User, Depends(require_user_permission("counselling:manage"))]
AdminUser = Annotated[User, Depends(require_user_permission("admin:manage"))]
StudentUser = Annotated[User, Depends(require_user_permission("counselling:request"))]
ChatActor = Annotated[Actor, Depends(require_permission("chat:use"))]
PeerActor = Annotated[Actor, Depends(require_permission("peer:match"))]
McpActor = Annotated[Actor, Depends(require_permission("mcp:use"))]
SafetyActor = Annotated[Actor, Depends(require_permission("safety:check"))]
VoiceUser = Annotated[User, Depends(require_user_permission("voice:use"))]
KnowledgeAdmin = Annotated[User, Depends(require_user_permission("knowledge:manage"))]
