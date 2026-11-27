"""Tests for short IDs, RBAC, voice preferences and pgvector knowledge."""

import os
import uuid
from contextlib import asynccontextmanager

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/opencode/campus_smoke.db"
os.makedirs("/tmp/opencode", exist_ok=True)

from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.university import University
from app.models.user import User
from app.orchestrator import graph
from app.services import knowledge_service, speech_service


@asynccontextmanager
async def client():
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c,
    ):
        yield c


async def university_public_id(slug: str) -> str:
    async with AsyncSessionLocal() as db:
        return (await db.scalar(select(University).where(University.slug == slug))).public_id


async def register(c, slug: str, domain: str, **profile) -> dict:
    body = {
        "email": f"{uuid.uuid4().hex[:12]}@{domain}",
        "password": "a-long-test-password",
        "full_name": "Test Student",
        "university_id": await university_public_id(slug),
        **profile,
    }
    resp = await c.post("/auth/register", json=body)
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def make_admin(c, slug: str, domain: str) -> dict:
    headers = await register(c, slug, domain)
    me = (await c.get("/auth/me", headers=headers)).json()
    async with AsyncSessionLocal() as db:
        await db.execute(update(User).where(User.public_id == me["id"]).values(role="admin"))
        await db.commit()
    return headers


async def test_ids_voice_preference_and_rbac():
    async with client() as c:
        headers = await register(
            c, "uon", "uonbi.ac.ke", gender="female", field_of_study="tech"
        )
        me = (await c.get("/auth/me", headers=headers)).json()
        assert len(me["id"]) == 5 and me["id"].isalnum() and me["id"].isupper()
        assert len(me["university_id"]) == 5
        assert me["voice_preference"] == "auto"

        changed = await c.patch(
            "/auth/me/voice", headers=headers, json={"preference": "male"}
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["voice_preference"] == "male"

        forbidden = await c.post("/knowledge", headers=headers, json={})
        assert forbidden.status_code == 403

        admin = await make_admin(c, "uon", "uonbi.ac.ke")
        denied = await c.patch(
            "/auth/me/voice", headers=admin, json={"preference": "female"}
        )
        assert denied.status_code == 200  # admins are allowed to use chat features too


async def test_voice_auto_uses_opposite_gender(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "elevenlabs_voice_id_female", "FEMALE-ID")
    monkeypatch.setattr(settings, "elevenlabs_voice_id_male", "MALE-ID")
    monkeypatch.setattr(settings, "elevenlabs_crisis_voice_id", "CALM-ID")
    assert speech_service.resolve_voice_id("auto", "female") == "MALE-ID"
    assert speech_service.resolve_voice_id("auto", "male") == "FEMALE-ID"
    assert speech_service.resolve_voice_id("female", "male") == "FEMALE-ID"
    assert speech_service.resolve_voice_id("auto", None) == "FEMALE-ID"
    assert speech_service.resolve_voice_id("auto", "female", crisis=True) == "CALM-ID"


async def test_knowledge_search_reaches_claude_context(monkeypatch):
    seen: list[list[dict]] = []

    async def fake_generate(messages, *args, **kwargs) -> str:
        seen.append(messages)
        return "Here is what the campus says."

    monkeypatch.setattr(graph, "generate_response", fake_generate)

    async with client() as c:
        admin = await make_admin(c, "uon", "uonbi.ac.ke")
        student = await register(c, "uon", "uonbi.ac.ke")

        created = await c.post(
            "/knowledge",
            headers=admin,
            json={
                "title": "Bursary application window",
                "content": "Applications for the bursary close on 30 November each year.",
                "source": "student finance office",
                "campus_wide": True,
            },
        )
        assert created.status_code == 201, created.text
        assert len(created.json()["id"]) == 5

        hits = await c.get("/knowledge/search", headers=student, params={"q": "bursary deadline"})
        assert hits.status_code == 200, hits.text
        assert hits.json()[0]["title"] == "Bursary application window"

        conv = await c.post("/conversations", headers=student, json={})
        turn = await c.post(
            "/conversations/chat",
            headers=student,
            json={
                "conversation_id": conv.json()["id"],
                "message": "When does the bursary application close?",
            },
        )
        assert turn.status_code == 200, turn.text
        assert seen, "Claude was not called"
        assert "Bursary application window" in seen[-1][0]["content"]
        assert "Campus knowledge" in seen[-1][0]["content"]

        async with AsyncSessionLocal() as db:
            direct = await knowledge_service.search(db, "bursary deadline")
            assert direct and direct[0].score > 0
