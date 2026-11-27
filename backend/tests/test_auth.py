"""Password and JWT unit tests."""

from uuid import uuid4

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.services.auth_service import hash_password, verify_password


def test_password_hash_roundtrip():
    hashed = hash_password("a-very-long-password-that-exceeds-bcrypts-72-byte-limit" * 2)

    assert hashed != "a-very-long-password"
    assert verify_password("a-very-long-password-that-exceeds-bcrypts-72-byte-limit" * 2, hashed)
    assert not verify_password("wrong-password", hashed)


def test_tokens_roundtrip_with_types():
    subject = str(uuid4())
    access = create_access_token(subject)
    refresh = create_refresh_token(subject)

    assert decode_token(access)["type"] == "access"
    assert decode_token(refresh)["type"] == "refresh"
    assert decode_token(access)["sub"] == subject
    assert decode_token("not-a-token") is None
