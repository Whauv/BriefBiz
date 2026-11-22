from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import close_db_engine, get_db_session
from app.main import app
from app.services.elasticsearch import close_elasticsearch
from app.services.openai_client import close_openai_client
from app.services.redis import close_redis


@pytest.fixture(autouse=True)
async def _reset_async_singletons() -> AsyncGenerator[None, None]:
    """Close module-global async clients/engine at the end of each test.

    ``get_redis``/``get_elasticsearch``/``get_openai_client`` cache a client the first
    time they are used (e.g. the auth rate limiter creates the Redis client), and
    ``AsyncSessionLocal`` binds to the module-global engine (used by the Celery
    workers). pytest runs each async test in its own event loop, so anything cached in
    one test's loop would be reused in the next with a closed loop. Resetting them here
    (inside the current test's loop) lets the next test recreate them cleanly.
    """
    yield
    await close_redis()
    await close_elasticsearch()
    await close_openai_client()
    await close_db_engine()


# ---------------------------------------------------------------------------
# Real-database fixtures (Postgres)
#
# The ORM models are Postgres-specific (JSONB, ARRAY, ``::jsonb`` server defaults),
# so tests run against a real Postgres instance rather than SQLite. CI provides one
# via a service container; locally use ``docker compose up -d postgres`` (or the
# ``docker compose --profile test run --rm api-test`` path). The connection string
# comes from ``DATABASE_URL`` through ``Settings``.
# ---------------------------------------------------------------------------


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """A fresh schema per test: drop + create before, drop after.

    ``NullPool`` avoids holding connections open across the DDL, which keeps
    ``drop_all`` from blocking on a lingering connection.
    """
    settings = get_settings()
    test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield test_engine
    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """A session for arranging/asserting DB state directly in a test."""
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session


@pytest.fixture
async def db_client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    """An ASGI client whose requests run against the real test database.

    Each request gets its own session (mirroring production) bound to the same
    per-test schema, so data seeded via ``db_session``/factories is visible to
    route handlers and vice versa.
    """
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with maker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()
