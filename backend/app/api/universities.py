"""Public list of universities for registration."""

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.university import University
from app.schemas.university import UniversityOut

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("", response_model=list[UniversityOut])
async def list_universities(db: DbSession):
    result = await db.execute(
        select(University).where(University.is_active.is_(True)).order_by(University.name)
    )
    return [UniversityOut.from_university(u) for u in result.scalars().all()]
