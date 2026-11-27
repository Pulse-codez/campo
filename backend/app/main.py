"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin,
    auth,
    conversations,
    counselling,
    decision,
    escalation,
    health,
    onboarding,
    policy,
    resources,
    safety,
    speech,
    study,
    universities,
)
from app.core.database import AsyncSessionLocal, engine
from app.models.base import Base
from app.services.seed import seed_universities


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience: create tables and seed universities. Production uses Alembic migrations.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_universities(db)
    yield
    await engine.dispose()


app = FastAPI(
    title="Campus Support Companion",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    counselling.router,
    speech.router,
    admin.router,
    safety.router,
    resources.router,
    escalation.router,
    study.router,
    decision.router,
    policy.router,
):
    app.include_router(router)


@app.get("/", tags=["health"])
async def root():
    return {"service": "campus-support-companion", "status": "ok", "version": "0.1.0"}
