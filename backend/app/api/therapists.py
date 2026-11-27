"""Concerns catalogue and virtual therapist recommendation."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser
from app.core.therapists import (
    CONCERNS,
    THERAPISTS,
    alternatives,
    normalise_concerns,
    recommend,
)
from app.schemas.therapist import ConcernOut, RecommendationOut, TherapistOut

router = APIRouter(tags=["therapists"])


class RecommendIn(BaseModel):
    concerns: list[str] = Field(default_factory=list, max_length=10)


def _out(t) -> TherapistOut:
    return TherapistOut(key=t.key, name=t.name, focus=t.focus)


@router.get("/concerns", response_model=list[ConcernOut])
async def list_concerns(user: CurrentUser):
    return [ConcernOut(key=k, label=v) for k, v in CONCERNS.items()]


@router.get("/therapists", response_model=list[TherapistOut])
async def list_therapists(user: CurrentUser):
    return [_out(t) for t in THERAPISTS.values()]


@router.post("/therapists/recommend", response_model=RecommendationOut)
async def recommend_therapist(body: RecommendIn, user: CurrentUser):
    concerns = normalise_concerns(body.concerns)
    primary = recommend(concerns)
    return RecommendationOut(
        primary=_out(primary),
        alternatives=[_out(t) for t in alternatives(concerns, primary)],
        show_crisis_resources="suicide" in concerns,
    )
