"""FastAPI application factory."""

from contextlib import asynccontextmanager

from anthropic import APIError, AuthenticationError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    admin,
    auth,
    checkin,
    conversations,
    counselling,
    decision,
    escalation,
    health,
    kindness,
    knowledge,
    onboarding,
    peer,
    policy,
    resources,
    safety,
    speech,
    study,
    therapists,
    universities,
)
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, engine
from app.models.base import Base
from app.services.seed import seed_universities


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience only. Production schema changes go through Alembic.
    if get_settings().app_env != "production":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal() as db:
            await seed_universities(db)
    yield
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title="rafiki-chat",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    health.router,
    universities.router,
    auth.router,
    onboarding.router,
    conversations.router,
    peer.router,
    counselling.router,
    checkin.router,
    kindness.router,
    speech.router,
    admin.router,
    safety.router,
    resources.router,
    escalation.router,
    study.router,
    therapists.router,
    decision.router,
    policy.router,
    knowledge.router,
):
    app.include_router(router)


@app.exception_handler(APIError)
async def anthropic_error_handler(request: Request, exc: APIError) -> JSONResponse:
    # Handled here (not as a 500) so the response still carries the CORS headers and the app can show a message.
    if isinstance(exc, AuthenticationError):
        return JSONResponse(status_code=503, content={"detail": "ai_auth_failed"})
    return JSONResponse(status_code=502, content={"detail": "ai_provider_error"})


@app.get("/", tags=["health"])
async def root():
    return {"service": "rafiki-chat", "status": "ok", "version": "0.1.0"}
