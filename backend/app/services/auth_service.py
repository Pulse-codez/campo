"""Auth service: university-scoped registration, login, token issue."""

import asyncio
import base64
import hashlib

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.models.university import University
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister
from app.services.id_service import find_by_public_id


def _password_bytes(password: str) -> bytes:
    """Pre-hash so bcrypt's 72-byte limit never truncates a password."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    # New hashes use the SHA-256 pre-hash; accept legacy raw bcrypt hashes too.
    for candidate in (_password_bytes(plain), plain.encode("utf-8")[:72]):
        try:
            if bcrypt.checkpw(candidate, hashed.encode("utf-8")):
                return True
        except (TypeError, ValueError):
            continue
    return False


async def hash_password_async(password: str) -> str:
    return await asyncio.to_thread(hash_password, password)


async def verify_password_async(plain: str, hashed: str) -> bool:
    return await asyncio.to_thread(verify_password, plain, hashed)


def email_matches_university(email: str, university: University) -> bool:
    domain = email.rsplit("@", 1)[-1].lower()
    return any(domain == d or domain.endswith("." + d) for d in university.domains)


async def register_student(db: AsyncSession, data: UserRegister) -> User:
    university = await find_by_public_id(db, University, data.university_id)
    if university is None or not university.is_active:
        raise ValueError("university_not_found")
    if not email_matches_university(data.email, university):
        raise ValueError("email_domain_not_allowed")

    existing = await db.scalar(select(User).where(User.email == data.email.lower()))
    if existing:
        raise ValueError("email_already_registered")

    user = User(
        email=data.email.lower(),
        password_hash=await hash_password_async(data.password),
        full_name=data.full_name,
        role="student",
        university_id=university.id,
        gender=data.gender,
        year_of_study=data.year_of_study,
        field_of_study=data.field_of_study,
        voice_preference=data.voice_preference,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, data: UserLogin) -> User | None:
    user = await db.scalar(select(User).where(User.email == data.email.lower()))
    if user is None or not await verify_password_async(data.password, user.password_hash):
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
