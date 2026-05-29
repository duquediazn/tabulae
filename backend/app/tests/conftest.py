"""
This file defines global pytest fixtures used across the test suite.

Pytest Execution Flow and Fixture Summary

1. Pytest discovers all test files (e.g., test_*.py) and functions (test_*).
2. Before running each test, it looks at its arguments (e.g., `client`, `session`).
3. For each argument, it finds and executes the matching fixture.
4. Fixtures are run in dependency order. Their return values are injected into the test.
5. After the test, any fixtures are cleaned up (if needed).
6. The process repeats for the next test.

By default, fixtures run once per test (`scope="function"`).
This ensures each test gets a clean environment.

Available fixture scopes:
- "function" (default): Run once per test function
- "class": Run once per test class
- "module": Run once per test file
- "session": Run once for the entire test session

In this project:
- `session` fixture resets the database before each test.
- `client` fixture provides a FastAPI TestClient using that session.
- `active_user`, `get_admin_headers`, etc., all depend on `session`, so they inherit a clean DB.
- `create_test_database` runs once per session to initialize tables.

This structure ensures:
- Full test isolation
- No leftover data between tests
- Stable and repeatable test runs
"""

from app.models.stock import Stock
import asyncio
import pytest
import pytest_asyncio
from sqlmodel import SQLModel, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.models.database import get_db
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.product_category import ProductCategory
from httpx import ASGITransport, AsyncClient
from app.main import app

# Connection string for the PostgreSQL test database.
# Reminder: inside Docker use db_test:5432; from the host machine use 127.0.0.1:5434.
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@db_test:5432/test_db"

# Create the test engine (async)
engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)
TestAsyncSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Create tables once before running any tests
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    This fixture runs once per test session to create tables if they don't exist.
    """
    async def _create():
        tmp_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        async with tmp_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        await tmp_engine.dispose()

    asyncio.run(_create())


# Create a fresh, clean session for each test
@pytest_asyncio.fixture()
async def session():
    """
    This fixture returns a clean AsyncSession and deletes all rows before each test.
    """
    async with TestAsyncSession() as session:
        # Clean tables before each test in correct FK order
        await session.execute(delete(StockMoveLine))
        await session.execute(delete(StockMove))
        await session.execute(delete(Stock))
        await session.execute(delete(Product))
        await session.execute(delete(User))
        await session.execute(delete(Warehouse))
        await session.execute(delete(ProductCategory))
        await session.execute(delete(RevokedToken))
        await session.commit()
        yield session


# Override FastAPI's get_db dependency with the test session
@pytest_asyncio.fixture()
async def client(session):
    """
    This fixture injects the test session into FastAPI via dependency override.
    It ensures all API routes use the same session used in the test.
    """

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def base_data(session):
    """Provides a default category, active warehouse, and active product for tests."""
    from types import SimpleNamespace

    category = ProductCategory(name="BaseCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="Base WH", is_active=True)
    product = Product(sku="BASESKU", short_name="Base Product", category_id=category.id, is_active=True)
    session.add_all([warehouse, product])
    await session.commit()

    return SimpleNamespace(category=category, warehouse=warehouse, product=product)
