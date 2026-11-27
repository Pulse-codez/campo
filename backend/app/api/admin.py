"""Admin endpoints: assign roles within the admin's own university."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import AdminUser, DbSession
from app.models.user import ROLES, User
from app.schemas.auth import UserOut
from app.services.audit_service import audit
from app.services.id_service import find_by_public_id

router = APIRouter(prefix="/admin", tags=["admin"])


class RoleIn(BaseModel):
    role: str


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def set_role(user_id: str, body: RoleIn, db: DbSession, admin: AdminUser):
    if body.role not in ROLES:
        raise HTTPException(status_code=422, detail="unknown_role")
    target = await find_by_public_id(db, User, user_id)
    if target is None or target.university_id != admin.university_id:
        raise HTTPException(status_code=404, detail="user_not_found")
    target.role = body.role
    audit(db, admin.id, "admin.role_changed", target=target.public_id, details=body.role)
    await db.commit()
    await db.refresh(target)
    await db.refresh(target, attribute_names=["university"])
    return UserOut.from_user(target)
