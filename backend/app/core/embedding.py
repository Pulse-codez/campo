"""Embeddings for campus knowledge.

Claude has no public embeddings API, so any OpenAI-compatible embeddings
endpoint can be configured with EMBEDDING_API_URL. When it is unset, a stable
local hashing embedding keeps development and tests fully offline.
"""

import hashlib
import math
import re

import httpx

from app.core.config import get_settings

EMBEDDING_DIM = 384  # matches the pgvector column in migration 0001


def _normalize(vector: list[float], dim: int = EMBEDDING_DIM) -> list[float]:
    sized = [float(value) for value in vector[:dim]]
    sized.extend([0.0] * (dim - len(sized)))
    norm = math.sqrt(sum(value * value for value in sized))
    if norm == 0:
        return sized
    return [value / norm for value in sized]


def _local_embedding(text: str) -> list[float]:
    """Deterministic bag-of-words embedding, suitable for offline development."""
    vector = [0.0] * EMBEDDING_DIM
    for token in re.findall(r"\w+", text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIM
        vector[index] += 1.0 + digest[4] / 255.0
    return _normalize(vector)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    if not settings.embedding_api_url:
        return [_local_embedding(text) for text in texts]

    payload: dict[str, object] = {
        "model": settings.embedding_model,
        "input": texts,
        "dimensions": EMBEDDING_DIM,
    }
    headers = {"Content-Type": "application/json"}
    if settings.embedding_api_key:
        headers["Authorization"] = f"Bearer {settings.embedding_api_key}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            settings.embedding_api_url, headers=headers, json=payload
        )
        response.raise_for_status()
        data = response.json()["data"]
    return [_normalize(item["embedding"]) for item in data]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))
