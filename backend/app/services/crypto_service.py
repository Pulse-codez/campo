"""AES-GCM field encryption for message bodies at rest.

Format: `v1:<nonce_b64>:<ciphertext_b64>`. Values without the `v1:` prefix are
returned untouched so pre-encryption rows remain readable during migration.
"""

import base64
import hashlib
import logging
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

logger = logging.getLogger(__name__)

PREFIX = "v1:"
_key: bytes | None = None


class DecryptionError(Exception):
    """Raised when a stored value cannot be decrypted with the current key."""


def _load_key() -> bytes:
    global _key
    if _key is not None:
        return _key

    settings = get_settings()
    if settings.field_encryption_key:
        _key = hashlib.sha256(settings.field_encryption_key.encode("utf-8")).digest()
    elif settings.app_env == "production":
        raise RuntimeError("FIELD_ENCRYPTION_KEY must be set in production")
    else:
        # Development fallback: ephemeral key, so restarts make old rows
        # unreadable. Set FIELD_ENCRYPTION_KEY for stable local development.
        logger.warning("FIELD_ENCRYPTION_KEY unset; using an ephemeral dev key")
        _key = os.urandom(32)
    return _key


def encrypt(text: str) -> str:
    nonce = os.urandom(12)
    ciphertext = AESGCM(_load_key()).encrypt(nonce, text.encode("utf-8"), None)
    return PREFIX + base64.b64encode(nonce).decode() + ":" + base64.b64encode(ciphertext).decode()


def decrypt(value: str) -> str:
    if not value.startswith(PREFIX):
        return value  # legacy plaintext row
    try:
        _, nonce_b64, ciphertext_b64 = value.split(":", 2)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        return AESGCM(_load_key()).decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception as exc:
        raise DecryptionError("message_could_not_be_decrypted") from exc
