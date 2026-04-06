from sqlmodel import SQLModel, create_engine, Session
from app.utils.getenv import get_required_env
import os

# Connect to the existing database
DATABASE_URL = get_required_env("DATABASE_URL")

echo = os.getenv("ENVIRONMENT", "development") != "production"
engine = create_engine(DATABASE_URL, echo=echo)


def get_db():
    """Yields a database session."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Creates the database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)
