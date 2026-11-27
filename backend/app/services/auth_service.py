"""Auth service: university-scoped registration, login, token issue."""

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.models.university import University
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def email_matches_university(email: str, university: University) -> bool:
    domain = email.rsplit("@", 1)[-1].lower()
    return any(domain == d or domain.endswith("." + d) for d in university.domains)


async def register_student(db: AsyncSession, data: UserRegister) -> User:
    university = await db.get(University, data.university_id)
    if university is None or not university.is_active:
        raise ValueError("university_not_found")
    if not email_matches_university(data.email, university):
        raise ValueError("email_domain_not_allowed")

    existing = await db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise ValueError("email_already_registered")

    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role="student",
        university_id=university.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, data: UserLogin) -> User | None:
    user = await db.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def tokens_for_user(user: User) -> TokenResponse:
    extra = {"role": user.role, "uni": str(user.university_id)}
    return TokenResponse(
        access_token=create_access_token(str(user.id), extra),
        refresh_token=create_refresh_token(str(user.id)),
    )
