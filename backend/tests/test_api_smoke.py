"""End-to-end API checks: university boundary, consent gating, crisis path, staff queue.

Runs against SQLite so no Postgres is needed. The conversation model is never called here:
the crisis path skips it by design, and the tests avoid non-crisis messages.
"""

import os
import uuid

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/opencode/campus_smoke.db"
os.makedirs("/tmp/opencode", exist_ok=True)
if os.path.exists("/tmp/opencode/campus_smoke.db"):
    os.remove("/tmp/opencode/campus_smoke.db")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.university import University
from app.models.user import User


@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


async def test_mcp_proxy_routes_require_credentials(client):
    """These routes must never be callable by an unauthenticated network client."""
    option = {"id": "a", "label": "Option A", "pros": ["calm"], "cons": ["slow"]}
    cases = [
        ("POST", "/safety/check", {"text": "I feel stressed"}),
        ("POST", "/resources/find", {"resource_type": "counselling"}),
        ("POST", "/escalation/request", {"reason": "test request"}),
        ("POST", "/study/plan", {"units": ["BIO 101"], "hours_per_week": 4}),
        (
            "POST",
            "/decision/evaluate",
            {"situation": "Choosing a path", "options": [option, {**option, "id": "b", "label": "Option B"}], "values": ["calm"]},
        ),
        ("GET", "/policies/search", None),
    ]
    for method, path, payload in cases:
        response = await client.request(
            method,
            path,
            json=payload,
            params={"q": "bursary"} if method == "GET" else None,
        )
        assert response.status_code == 401, (path, response.status_code, response.text)


async def uni_id(slug: str) -> str:
    async with AsyncSessionLocal() as db:
        uni = await db.scalar(select(University).where(University.slug == slug))
        return uni.public_id


async def register(client, slug: str, email_domain: str) -> dict:
    email = f"{uuid.uuid4().hex[:10]}@{email_domain}"
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "longpassword1",
            "full_name": "Test Person",
            "university_id": await uni_id(slug),
        },
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def onboard(client, headers, counselling: bool, concerns=("stress",)) -> dict:
    resp = await client.post(
        "/onboarding",
        headers=headers,
        json={
            "concerns": list(concerns),
            "consents": {"counselling": counselling},
            "policy_version": "v1.0",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


async def make_staff(client, slug: str, domain: str, role: str) -> dict:
    headers = await register(client, slug, domain)
    me = (await client.get("/auth/me", headers=headers)).json()
    async with AsyncSessionLocal() as db:
        internal_id = await db.scalar(select(User.id).where(User.public_id == me["id"]))
        await db.execute(update(User).where(User.id == internal_id).values(role=role))
        await db.commit()
    return headers


async def test_universities_are_seeded(client):
    resp = await client.get("/universities")
    assert resp.status_code == 200
    slugs = {u["slug"] for u in resp.json()}
    assert {"uon", "ku", "jkuat"} <= slugs


async def test_registration_requires_university_email(client):
    resp = await client.post(
        "/auth/register",
        json={
            "email": f"{uuid.uuid4().hex[:8]}@gmail.com",
            "password": "longpassword1",
            "university_id": await uni_id("uon"),
        },
    )
    assert resp.status_code == 422
    assert resp.json()["detail"] == "email_domain_not_allowed"


async def test_student_onboarding_and_counselling_request(client):
    headers = await register(client, "uon", "uonbi.ac.ke")
    me = (await client.get("/auth/me", headers=headers)).json()
    assert me["onboarded"] is False and me["role"] == "student"

    # Counselling request is refused until consent is given.
    denied = await client.post(
        "/counselling-sessions", headers=headers, json={"topic": "exam stress"}
    )
    assert denied.status_code == 403
    assert denied.json()["detail"] == "counselling_consent_required"

    await onboard(client, headers, counselling=True)
    me = (await client.get("/auth/me", headers=headers)).json()
    assert me["onboarded"] is True

    created = await client.post(
        "/counselling-sessions", headers=headers, json={"topic": "exam stress"}
    )
    assert created.status_code == 201
    assert created.json()["status"] == "requested"


async def test_crisis_message_gets_protocol_without_model(client):
    headers = await register(client, "uon", "uonbi.ac.ke")
    resp = await client.post(
        "/conversations/chat",
        headers=headers,
        json={"message": "I want to kill myself"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["risk_level"] == "crisis"
    assert body["requires_human"] is True
    assert "1199" in body["assistant_content"]


async def test_staff_queue_is_limited_to_own_university_and_consent(client):
    student = await register(client, "uon", "uonbi.ac.ke")
    await onboard(client, student, counselling=True)
    created = await client.post(
        "/counselling-sessions", headers=student, json={"topic": "sleep"}
    )
    session_id = created.json()["id"]

    same_uni = await make_staff(client, "uon", "uonbi.ac.ke", "counsellor")
    other_uni = await make_staff(client, "jkuat", "jkuat.ac.ke", "counsellor")

    queue = (await client.get("/counselling-sessions", headers=same_uni)).json()
    assert any(s["id"] == session_id for s in queue)

    other_queue = (await client.get("/counselling-sessions", headers=other_uni)).json()
    assert all(s["id"] != session_id for s in other_queue)

    forbidden = await client.patch(
        f"/counselling-sessions/{session_id}", headers=other_uni, json={"status": "booked"}
    )
    assert forbidden.status_code == 404

    accepted = await client.patch(
        f"/counselling-sessions/{session_id}", headers=same_uni, json={"status": "booked"}
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "booked"


async def test_students_cannot_open_the_staff_queue_actions(client):
    student = await register(client, "uon", "uonbi.ac.ke")
    await onboard(client, student, counselling=True)
    created = await client.post(
        "/counselling-sessions", headers=student, json={"topic": "sleep"}
    )
    resp = await client.patch(
        f"/counselling-sessions/{created.json()['id']}",
        headers=student,
        json={"status": "booked"},
    )
    assert resp.status_code == 403


async def test_revoked_consent_hides_request_from_staff(client):
    student = await register(client, "ku", "ku.ac.ke")
    await onboard(client, student, counselling=True)
    created = await client.post("/counselling-sessions", headers=student, json={"topic": "sleep"})
    session_id = created.json()["id"]

    staff = await make_staff(client, "ku", "ku.ac.ke", "peer_counsellor")
    before = (await client.get("/counselling-sessions", headers=staff)).json()
    assert any(s["id"] == session_id for s in before)

    revoked = await client.post(
        "/consents", headers=student, json={"scope": "counselling", "granted": False}
    )
    assert revoked.status_code == 201

    after = (await client.get("/counselling-sessions", headers=staff)).json()
    assert all(s["id"] != session_id for s in after)


async def test_concerns_list_is_public_to_authenticated_users(client):
    headers = await register(client, "uon", "uonbi.ac.ke")
    resp = await client.get("/concerns", headers=headers)
    assert resp.status_code == 200
    assert {c["key"] for c in resp.json()} == {"family_issues", "stress", "peer_pressure", "suicide", "other"}


async def test_recommendation_prioritises_safety(client):
    headers = await register(client, "uon", "uonbi.ac.ke")
    resp = await client.post(
        "/therapists/recommend", headers=headers, json={"concerns": ["stress", "suicide"]}
    )
    body = resp.json()
    assert body["primary"]["key"] == "steady"
    assert body["show_crisis_resources"] is True


async def test_onboarding_stores_recommended_therapist(client):
    headers = await register(client, "uon", "uonbi.ac.ke")
    user = await onboard(client, headers, counselling=False, concerns=("family_issues",))
    assert user["therapist_key"] == "bridge"
    assert user["concerns"] == ["family_issues"]


async def test_onboarding_requires_a_concern(client):
    headers = await register(client, "uon", "uonbi.ac.ke")
    resp = await client.post(
        "/onboarding",
        headers=headers,
        json={"concerns": [], "consents": {}, "policy_version": "v1.0"},
    )
    assert resp.status_code == 422


async def test_listed_universities_are_available(client):
    resp = await client.get("/universities")
    names = {u["slug"] for u in resp.json()}
    assert {"uon", "kca", "strathmore", "tuk", "zetech", "daystar", "riara", "other"} <= names


async def test_other_university_requires_name_and_academic_email(client):
    other = await uni_id("other")
    base = {"password": "longpassword1", "university_id": other}

    missing_name = await client.post(
        "/auth/register", json={**base, "email": f"{uuid.uuid4().hex[:8]}@gmail.com"}
    )
    assert missing_name.json()["detail"] == "other_university_name_required"

    not_academic = await client.post(
        "/auth/register",
        json={**base, "email": f"{uuid.uuid4().hex[:8]}@gmail.com", "other_university_name": "Mount Kenya"},
    )
    assert not_academic.json()["detail"] == "other_email_not_accepted"

    ok = await client.post(
        "/auth/register",
        json={**base, "email": f"{uuid.uuid4().hex[:8]}@mku.ac.ke", "other_university_name": "Mount Kenya University"},
    )
    assert ok.status_code == 201, ok.text
