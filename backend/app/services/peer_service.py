"""Peer matching and relay. Messages are screened for crisis and stored encrypted."""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Actor
from app.models.conversation import Conversation
from app.models.peer_match import PeerMatch
from app.orchestrator.protocol import CRISIS_PROTOCOL_MESSAGE
from app.safety.classifier import assess as classify
from app.safety.rules.engine import apply as apply_rules
from app.schemas.conversation import ConversationCreate, MessageOut
from app.schemas.peer import PeerMatchOut, PeerMessageOut
from app.services.audit_service import audit
from app.services.conversation_service import (
    add_message,
    create_conversation,
    get_messages,
    hash_anonymous_token,
    new_anonymous_token,
)
from app.services.id_service import find_by_public_id


def _conversation_key(actor: Actor) -> str | None:
    return hash_anonymous_token(actor.anonymous_token) if actor.anonymous_token else None


async def to_out(
    db: AsyncSession,
    match: PeerMatch,
    anonymous_token: str | None = None,
    conversation_public_id: str | None = None,
) -> PeerMatchOut:
    if conversation_public_id is None:
        conv = await db.get(Conversation, match.conversation_id)
        conversation_public_id = conv.public_id if conv else str(match.conversation_id)
    peer_label = None
    if match.status == "matched":
        peer_label = (
            "A peer in your field"
            if match.peer_id or match.counterpart_conversation_id
            else None
        )
    return PeerMatchOut(
        id=match.public_id,
        conversation_id=conversation_public_id,
        topic=match.topic,
        field_of_study=match.field_of_study,
        year_of_study=match.year_of_study,
        status=match.status,
        matched_at=match.matched_at,
        peer_label=peer_label,
        anonymous_token=anonymous_token,
    )


async def _accessible(db: AsyncSession, match: PeerMatch, actor: Actor) -> bool:
    if actor.id is not None:
        return actor.id in (match.seeker_id, match.peer_id)
    key = _conversation_key(actor)
    if not key:
        return False
    conversation_ids = [match.conversation_id]
    if match.counterpart_conversation_id:
        conversation_ids.append(match.counterpart_conversation_id)
    result = await db.scalar(
        select(Conversation.id).where(
            Conversation.id.in_(conversation_ids),
            Conversation.anonymous_token_hash == key,
        )
    )
    return result is not None


async def _try_match(db: AsyncSession, match: PeerMatch) -> None:
    """Match by field and near year; never match a student with themselves."""
    stmt = select(PeerMatch).where(
        PeerMatch.status == "searching",
        PeerMatch.id != match.id,
        PeerMatch.field_of_study == match.field_of_study,
    )
    candidates = (await db.execute(stmt)).scalars().all()
    for candidate in candidates:
        if match.seeker_id and candidate.seeker_id == match.seeker_id:
            continue
        if (
            None not in (match.year_of_study, candidate.year_of_study)
            and abs(match.year_of_study - candidate.year_of_study) > 1  # type: ignore[operator]
        ):
            continue
        now = datetime.now(UTC)
        match.status = candidate.status = "matched"
        match.matched_at = candidate.matched_at = now
        match.peer_id = candidate.seeker_id
        candidate.peer_id = match.seeker_id
        match.counterpart_conversation_id = candidate.conversation_id
        candidate.counterpart_conversation_id = match.conversation_id
        audit(
            db,
            match.seeker_id,
            "peer.match_created",
            target=str(match.id),
            details=json.dumps({"counterpart": str(candidate.id)}),
        )
        audit(
            db,
            candidate.seeker_id,
            "peer.match_created",
            target=str(candidate.id),
            details=json.dumps({"counterpart": str(match.id)}),
        )
        await db.commit()
        return


async def request_match(
    db: AsyncSession,
    actor: Actor,
    topic: str,
    field_of_study: str,
    year_of_study: int | None,
) -> PeerMatchOut:
    token = None if actor.id else (actor.anonymous_token or new_anonymous_token())
    conv = await create_conversation(
        db,
        actor.id,
        ConversationCreate(title=topic[:255], mode="peer"),
        anonymous_token=token,
    )
    conversation = await find_by_public_id(db, Conversation, conv.id)
    if conversation is None:  # pragma: no cover - just created above
        raise LookupError("conversation_not_found")
    match = PeerMatch(
        conversation_id=conversation.id,
        seeker_id=actor.id,
        topic=topic,
        field_of_study=field_of_study,
        year_of_study=year_of_study
        if year_of_study is not None
        else (actor.user.year_of_study if actor.user else None),
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    await _try_match(db, match)
    await db.refresh(match)
    return await to_out(db, match, token if token and not actor.anonymous_token else None, conv.id)


async def get_match(db: AsyncSession, match_id: str) -> PeerMatch | None:
    return await find_by_public_id(db, PeerMatch, match_id)


async def require_match(db: AsyncSession, match_id: str, actor: Actor) -> PeerMatch:
    match = await get_match(db, match_id)
    if match is None or not await _accessible(db, match, actor):
        raise LookupError("peer_match_not_found")
    return match


async def list_messages(db: AsyncSession, match: PeerMatch, actor: Actor) -> list[MessageOut]:
    conversation_id = match.conversation_id
    if actor.id is not None and actor.id == match.peer_id and match.counterpart_conversation_id:
        conversation_id = match.counterpart_conversation_id
    elif actor.id is None and match.counterpart_conversation_id:
        key = _conversation_key(actor)
        own = await db.scalar(
            select(Conversation.id).where(
                Conversation.id == match.conversation_id,
                Conversation.anonymous_token_hash == key,
            )
        )
        if own is None:
            conversation_id = match.counterpart_conversation_id
    return await get_messages(db, conversation_id, limit=100)


async def post_message(
    db: AsyncSession, match: PeerMatch, actor: Actor, content: str
) -> PeerMessageOut:
    applied = apply_rules(classify(content), {"previous_level": None})
    role = "seeker" if actor.id == match.seeker_id or actor.id is None else "peer"

    if applied["requires_human"]:
        # A peer cannot be the safety net. Break the relay and show the protocol.
        written = await add_message(db, match.conversation_id, "assistant", CRISIS_PROTOCOL_MESSAGE)
        if match.counterpart_conversation_id:
            await add_message(
                db, match.counterpart_conversation_id, "assistant", CRISIS_PROTOCOL_MESSAGE
            )
        audit(
            db,
            actor.id,
            "peer.message_escalated",
            target=str(match.id),
            details=json.dumps({"risk_level": applied["level"]}),
        )
        await db.commit()
        return PeerMessageOut.model_validate(written)

    written = await add_message(db, match.conversation_id, role, content)
    if match.counterpart_conversation_id:
        counterpart_role = "peer" if role == "seeker" else "seeker"
        await add_message(
            db,
            match.counterpart_conversation_id,
            counterpart_role,
            content,
            applied["level"],
        )
    return PeerMessageOut.model_validate(written)


async def close_match(db: AsyncSession, match: PeerMatch) -> None:
    match.status = "closed"
    if match.counterpart_conversation_id:
        counterpart = await db.scalar(
            select(PeerMatch).where(
                PeerMatch.conversation_id == match.counterpart_conversation_id
            )
        )
        if counterpart:
            counterpart.status = "closed"
    audit(db, match.seeker_id, "peer.match_closed", target=str(match.id))
    await db.commit()
