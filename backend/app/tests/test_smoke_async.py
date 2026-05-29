"""
Smoke test for the async stack.
Verifies that the async engine, session, and authenticated endpoint work end-to-end.

Run with:
    pytest backend/app/tests/test_smoke_async.py -v
(requires db_test running: docker compose -f docker-compose.dev.yml --profile test up db_test)
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.main import app
from app.models.database import get_db
from app.models.user import User
from app.utils.authentication import ACCESS_TOKEN_DURATION, create_access_token, hash_password
from datetime import timedelta

# Reminder: inside Docker use db_test:5432; from the host machine use 127.0.0.1:5434.
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@db_test:5432/test_db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestAsyncSession = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    async def _create():
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create())


@pytest_asyncio.fixture
async def async_session():
    async with TestAsyncSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_smoke_get_profile(client, async_session):
    """Verifica que el stack async funciona end-to-end con un endpoint autenticado."""
    user = User(
        name="Smoke",
        email="smoke@test.com",
        password=hash_password("pass"),
        role="user",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_DURATION),
    )
    response = await client.get(
        "/auth/profile", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "smoke@test.com"
