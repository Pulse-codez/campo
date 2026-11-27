"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    conversations,
    decision,
    escalation,
    health,
    policy,
    resources,
    safety,
    study,
)
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (Alembic manages migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Campus Support Companion",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(safety.router)
app.include_router(resources.router)
app.include_router(escalation.router)
app.include_router(study.router)
app.include_router(decision.router)
app.include_router(policy.router)

@app.get("/", tags=["health"])
async def root():
    return {"service": "campus-support-companion", "status": "ok", "version": "0.1.0"}
