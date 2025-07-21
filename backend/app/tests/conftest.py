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

from app.tests.utils import create_user_in_db
from app.models.stock import Stock
import pytest
from sqlmodel import SQLModel, create_engine, Session, delete
from app.models.database import get_db
from app.models.user import User
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.main import app

# Connection string for the PostgreSQL test database
TEST_DATABASE_URL = "postgresql://test_user:test_pass@db_test:5432/test_db"

# Create the test engine (SQLModel)
engine = create_engine(TEST_DATABASE_URL, echo=True)


# Create tables once before running any tests
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    This fixture runs once per test session to create tables if they don't exist.
    """
    SQLModel.metadata.create_all(engine)


# Create a fresh, clean session for each test
@pytest.fixture()
def session():
    """
    This fixture returns a clean SQLModel session and deletes all users before each test.
    You can expand it to clear more tables (e.g., products, stock).
    """
    with Session(engine) as session:
        # Clean tables before each test in correct FK order
        session.exec(delete(StockMoveLine))
        session.exec(delete(StockMove))
        session.exec(delete(Stock))
        session.exec(delete(Product))
        session.exec(delete(User))
        session.exec(delete(Warehouse))
        session.exec(delete(ProductCategory))
        session.commit()
        yield session


# Override FastAPI's get_db dependency with the test session
@pytest.fixture()
def client(session):
    """
    This fixture injects the test session into FastAPI via dependency override.
    It ensures all API routes use the same session used in the test.
    """

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
