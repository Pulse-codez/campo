"""Regression tests for anonymous chats, encrypted storage, peers and MCP context."""

import os
import uuid
from contextlib import asynccontextmanager
from types import SimpleNamespace

# This suite reuses the smoke-test database so the already-imported app engine matches.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/opencode/campus_smoke.db"
os.makedirs("/tmp/opencode", exist_ok=True)

from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.audit_log import AuditLog
from app.models.message import Message
from app.orchestrator import graph
from app.services import speech_service
from app.services.context_service import SupportContext


@asynccontextmanager
async def client():
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c,
    ):
        yield c


async def university_id(slug: str) -> str:
    async with AsyncSessionLocal() as db:
        from app.models.university import University

        uni = (await db.execute(select(University).where(University.slug == slug))).scalar_one()
        return str(uni.id)


async def register(c, slug: str, domain: str, **profile) -> dict:
    email = f"{uuid.uuid4().hex[:12]}@{domain}"
    body = {
        "email": email,
        "password": "a-long-test-password",
        "full_name": "Test Student",
        "university_id": await university_id(slug),
        **profile,
    }
    resp = await c.post("/auth/register", json=body)
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def test_anonymous_chat_is_encrypted_at_rest():
    async with client() as c:
        created = await c.post(
            "/conversations/anonymous",
            json={"field_of_study": "art", "year_of_study": 2},
        )
        assert created.status_code == 201, created.text
        conv = created.json()
        token = conv["anonymous_token"]
        headers = {"X-Anonymous-Token": token}

        turn = await c.post(
            "/conversations/chat",
            headers=headers,
            json={"message": "I want to kill myself", "conversation_id": conv["id"]},
        )
        assert turn.status_code == 200, turn.text
        assert turn.json()["risk_level"] == "crisis"
        assert "1199" in turn.json()["assistant_content"]

        async with AsyncSessionLocal() as db:
            row = await db.scalar(
                select(Message).where(Message.public_id == turn.json()["user_message_id"])
            )
            assert row.content.startswith("v1:")
            assert "kill myself" not in row.content

        history = await c.get(f"/conversations/{conv['id']}/messages", headers=headers)
        assert history.status_code == 200
        assert any(m["content"] == "I want to kill myself" for m in history.json())

        denied = await c.get(f"/conversations/{conv['id']}/messages")
        assert denied.status_code == 401
        stranger = await c.get(
            f"/conversations/{conv['id']}/messages",
            headers={"X-Anonymous-Token": "not-the-token"},
        )
        assert stranger.status_code == 404


async def test_profile_fields_register_and_mcp_context_reaches_claude(monkeypatch):
    seen: list[list[dict]] = []

    async def fake_gather(
        query: str, risk_level: str = "none", university_id=None
    ) -> SupportContext:
        return SupportContext(
            policies=[
                SimpleNamespace(
                    title="Mental health leave policy",
                    summary="You can request temporary academic accommodation.",
                    contact_email="wellbeing@uonbi.ac.ke",
                )
            ],
            resources=[
                SimpleNamespace(
                    name="Campus Counselling Centre",
                    contact="+254 700 000 100",
                    hours="weekdays 8am-5pm",
                )
            ],
        )

    async def fake_generate(messages, *args, **kwargs) -> str:
        seen.append(messages)
        return "I found support options for you."

    monkeypatch.setattr(graph.context_service, "gather_context", fake_gather)
    monkeypatch.setattr(graph, "generate_response", fake_generate)

    async with client() as c:
        headers = await register(
            c,
            "uon",
            "uonbi.ac.ke",
            gender="female",
            year_of_study=3,
            field_of_study="tech",
        )
        me = (await c.get("/auth/me", headers=headers)).json()
        assert me["gender"] == "female" and me["field_of_study"] == "tech"

        created = await c.post("/conversations", headers=headers, json={})
        conv_id = created.json()["id"]
        text_turn = await c.post(
            "/conversations/chat",
            headers=headers,
            json={"conversation_id": conv_id, "message": "I am stressed about exams"},
        )
        assert text_turn.status_code == 200, text_turn.text
        assert seen, "Claude was not called"
        system = seen[-1][0]["content"]
        assert "Mental health leave policy" in system
        assert "Campus Counselling Centre" in system
        assert seen[-1][-1] == {"role": "user", "content": "I am stressed about exams"}

        async def fake_transcribe(audio, filename, content_type) -> str:
            assert audio == b"fake-audio"
            return "Can you help with accommodation?"

        monkeypatch.setattr(speech_service, "transcribe", fake_transcribe)
        voice = await c.post(
            f"/conversations/{conv_id}/voice",
            headers=headers,
            files={"audio": ("speech.webm", b"fake-audio", "audio/webm")},
        )
        assert voice.status_code == 200, voice.text
        assert voice.json()["transcript"] == "Can you help with accommodation?"
        assert "Mental health leave policy" in seen[-1][0]["content"]

        unsupported = await c.post(
            f"/conversations/{conv_id}/voice",
            headers=headers,
            files={"audio": ("notes.txt", b"hello", "text/plain")},
        )
        assert unsupported.status_code == 415


async def test_peer_match_relays_messages_and_stops_at_crisis():
    async with client() as c:
        seeker = await register(
            c,
            "uon",
            "uonbi.ac.ke",
            gender="male",
            year_of_study=3,
            field_of_study="tech",
        )
        peer = await register(
            c,
            "uon",
            "uonbi.ac.ke",
            gender="female",
            year_of_study=4,
            field_of_study="tech",
        )

        first = await c.post(
            "/peer/matches",
            headers=seeker,
            json={"topic": "exam stress", "field_of_study": "tech", "year_of_study": 3},
        )
        second = await c.post(
            "/peer/matches",
            headers=peer,
            json={"topic": "exam stress", "field_of_study": "tech", "year_of_study": 4},
        )
        assert first.status_code == 201, first.text
        assert second.status_code == 201, second.text
        match_id = second.json()["id"]
        assert second.json()["status"] == "matched"
        first_now = await c.get(f"/peer/matches/{first.json()['id']}", headers=seeker)
        assert first_now.status_code == 200 and first_now.json()["status"] == "matched"

        normal = await c.post(
            f"/peer/matches/{match_id}/messages",
            headers=seeker,
            json={"content": "I failed a test and feel behind."},
        )
        assert normal.status_code == 201, normal.text

        relayed = await c.get(f"/peer/matches/{match_id}/messages", headers=peer)
        assert relayed.status_code == 200, relayed.text
        assert any("feel behind" in m["content"] for m in relayed.json())

        crisis = await c.post(
            f"/peer/matches/{match_id}/messages",
            headers=peer,
            json={"content": "I want to die"},
        )
        assert crisis.status_code == 201, crisis.text
        assert "1199" in crisis.json()["content"]

        seeker_view = await c.get(f"/peer/matches/{match_id}/messages", headers=seeker)
        assert any(
            "1199" in m["content"] and m["role"] == "assistant" for m in seeker_view.json()
        )

        stranger = await register(c, "ku", "ku.ac.ke", field_of_study="tech")
        forbidden = await c.get(f"/peer/matches/{match_id}/messages", headers=stranger)
        assert forbidden.status_code == 404

        async with AsyncSessionLocal() as db:
            audit = (
                await db.execute(
                    select(AuditLog).where(AuditLog.action == "peer.message_escalated")
                )
            ).scalars().first()
            assert audit is not None


async def test_mcp_proxy_requires_actor():
    async with client() as c:
        denied = await c.post("/escalation/request", json={"reason": "need help"})
        assert denied.status_code == 401

        headers = await register(c, "uon", "uonbi.ac.ke")
        # No MCP server is needed to prove the auth boundary: a failure is 502, not 401.
        proxied = await c.post(
            "/escalation/request",
            headers=headers,
            json={"reason": "need help", "urgency": "urgent"},
        )
        assert proxied.status_code in (200, 502)
