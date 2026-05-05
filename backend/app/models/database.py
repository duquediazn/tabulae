from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from app.utils.getenv import get_required_env

DATABASE_URL = get_required_env("DATABASE_URL")

echo = get_required_env("ENVIRONMENT", fallback="development") != "production"
engine = create_async_engine(DATABASE_URL, echo=echo)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """Yields an asynchronous database session for use in API endpoints."""
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables() -> None:
    """Creates the database tables based on the defined SQLModel models. Should be called at application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
