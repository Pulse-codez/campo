"""Peer support endpoints: find a student with shared experience and relay messages."""

from fastapi import APIRouter, HTTPException

from app.api.deps import DbSession, PeerActor
from app.schemas.peer import (
    PeerMatchCreate,
    PeerMatchOut,
    PeerMessageIn,
    PeerMessageOut,
)
from app.services import peer_service

router = APIRouter(prefix="/peer", tags=["peer"])


@router.post("/matches", response_model=PeerMatchOut, status_code=201)
async def request_match(body: PeerMatchCreate, db: DbSession, actor: PeerActor):
    return await peer_service.request_match(
        db,
        actor,
        topic=body.topic,
        field_of_study=body.field_of_study,
        year_of_study=body.year_of_study,
    )


@router.get("/matches/{match_id}", response_model=PeerMatchOut)
async def get_match(match_id: str, db: DbSession, actor: PeerActor):
    try:
        match = await peer_service.require_match(db, match_id, actor)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return await peer_service.to_out(db, match)


@router.get("/matches/{match_id}/messages", response_model=list[PeerMessageOut])
async def list_messages(match_id: str, db: DbSession, actor: PeerActor):
    try:
        match = await peer_service.require_match(db, match_id, actor)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return await peer_service.list_messages(db, match, actor)


@router.post("/matches/{match_id}/messages", response_model=PeerMessageOut, status_code=201)
async def post_message(match_id: str, body: PeerMessageIn, db: DbSession, actor: PeerActor):
    try:
        match = await peer_service.require_match(db, match_id, actor)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return await peer_service.post_message(db, match, actor, body.content)


@router.post("/matches/{match_id}/close", response_model=PeerMatchOut)
async def close_match(match_id: str, db: DbSession, actor: PeerActor):
    try:
        match = await peer_service.require_match(db, match_id, actor)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await peer_service.close_match(db, match)
    return await peer_service.to_out(db, match)
