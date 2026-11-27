"""Admin endpoints: assign roles within the admin's own university."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import AdminUser, DbSession
from app.models.user import ROLES, User
from app.schemas.auth import UserOut
from app.services.audit_service import audit

router = APIRouter(prefix="/admin", tags=["admin"])


class RoleIn(BaseModel):
    role: str


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def set_role(user_id: UUID, body: RoleIn, db: DbSession, admin: AdminUser):
    if body.role not in ROLES:
        raise HTTPException(status_code=422, detail="unknown_role")
    target = await db.get(User, user_id)
    if target is None or target.university_id != admin.university_id:
        raise HTTPException(status_code=404, detail="user_not_found")
    target.role = body.role
    audit(db, admin.id, "admin.role_changed", target=str(target.id), details=body.role)
    await db.commit()
    await db.refresh(target)
    return target
