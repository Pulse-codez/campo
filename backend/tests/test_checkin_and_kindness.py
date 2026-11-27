"""Monthly check-in window rules, check-in routes, kind notes, and kind message routes."""

import uuid
from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import app
from app.services.checkin_service import check_writable, is_open_now, writable_periods


def test_window_opens_in_last_seven_days_of_month():
    assert is_open_now("2026-11", date(2026, 11, 23)) is False
    assert is_open_now("2026-11", date(2026, 11, 24)) is True
    assert is_open_now("2026-11", date(2026, 11, 30)) is True


def test_past_months_are_always_open_for_catch_up():
    assert is_open_now("2026-10", date(2026, 11, 5)) is True


def test_writable_periods_skip_submitted_months():
    today = date(2026, 11, 27)
    open_now = writable_periods(today, submitted={"2026-11"})
    assert "2026-11" not in open_now
    assert "2026-10" in open_now


def test_check_writable_reasons():
    today = date(2026, 11, 27)
    assert check_writable("2026-12", today, set()).reason == "period_in_future"
    assert check_writable("2026-11", today, {"2026-11"}).reason == "already_submitted"
    assert check_writable("2026-01", today, set()).reason == "period_too_old"
    assert check_writable("2026-11", date(2026, 11, 10), set()).reason == "opens_in_last_week_of_month"


@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


async def signed_in(client) -> dict:
    slug_id = (await client.get("/universities")).json()[0]["id"]
    email = f"{uuid.uuid4().hex[:10]}@uonbi.ac.ke"
    resp = await client.post(
        "/auth/register",
        json={"email": email, "password": "longpassword1", "university_id": slug_id},
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def test_checkin_saves_once_per_period(client):
    headers = await signed_in(client)
    body = {"period": "2026-09", "feelings": "Tired but steady.", "direction": "Finishing my degree."}
    first = await client.post("/checkin", headers=headers, json=body)
    assert first.status_code == 201, first.text
    assert first.json()["requires_human"] is False

    again = await client.post("/checkin", headers=headers, json=body)
    assert again.status_code == 409
    assert again.json()["detail"] == "already_submitted"

    status = (await client.get("/checkin/status", headers=headers)).json()
    assert "2026-09" in status["submitted_periods"]


async def test_checkin_refuses_future_period(client):
    headers = await signed_in(client)
    resp = await client.post(
        "/checkin", headers=headers, json={"period": "2099-01", "feelings": "x", "direction": "y"}
    )
    assert resp.status_code == 422
    assert resp.json()["detail"] == "period_in_future"


async def test_checkin_crisis_text_flags_human_contacts(client):
    headers = await signed_in(client)
    resp = await client.post(
        "/checkin",
        headers=headers,
        json={"period": "2026-08", "feelings": "I want to kill myself", "direction": "nowhere"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["requires_human"] is True
    assert any("1199" in c for c in body["contacts"])


async def test_kind_message_needs_ai_key(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    get_settings.cache_clear()
    headers = await signed_in(client)
    resp = await client.post("/kindness/message", headers=headers, json={"theme": "hope"})
    assert resp.status_code == 503
    assert resp.json()["detail"] == "ai_not_configured"
    get_settings.cache_clear()


async def test_kind_message_returns_model_text(client, monkeypatch):
    from app.services import kindness_service

    async def fake_generate(messages, **kwargs):
        assert messages[0]["role"] == "system"
        return "  You are doing better than you think.  "

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    get_settings.cache_clear()
    monkeypatch.setattr(kindness_service, "generate_response", fake_generate)
    headers = await signed_in(client)
    resp = await client.post("/kindness/message", headers=headers, json={"theme": "rest"})
    get_settings.cache_clear()
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"message": "You are doing better than you think.", "theme": "rest"}


async def test_kind_notes_are_private_to_their_writer(client):
    owner = await signed_in(client)
    other = await signed_in(client)
    created = await client.post(
        "/kindness/notes", headers=owner, json={"recipient": "Wanjiku", "body": "Thank you for listening."}
    )
    assert created.status_code == 201
    note_id = created.json()["id"]

    mine = (await client.get("/kindness/notes", headers=owner)).json()
    assert any(n["id"] == note_id for n in mine)
    theirs = (await client.get("/kindness/notes", headers=other)).json()
    assert all(n["id"] != note_id for n in theirs)

    forbidden = await client.delete(f"/kindness/notes/{note_id}", headers=other)
    assert forbidden.status_code == 404
    deleted = await client.delete(f"/kindness/notes/{note_id}", headers=owner)
    assert deleted.status_code == 204


async def test_ai_auth_failure_returns_cors_safe_503(client, monkeypatch):
    import httpx
    from anthropic import AuthenticationError

    from app.services import kindness_service

    async def rejected(messages, **kwargs):
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        raise AuthenticationError(
            "Invalid bearer token", response=httpx.Response(401, request=request), body=None
        )

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    get_settings.cache_clear()
    monkeypatch.setattr(kindness_service, "generate_response", rejected)
    headers = await signed_in(client)
    resp = await client.post(
        "/kindness/message", headers={**headers, "Origin": "http://localhost:3001"}, json={"theme": "hope"}
    )
    get_settings.cache_clear()
    assert resp.status_code == 503
    assert resp.json()["detail"] == "ai_auth_failed"
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3001"
