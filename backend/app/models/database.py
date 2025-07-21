from sqlmodel import SQLModel, create_engine, Session
from app.utils.getenv import get_required_env

# Connect to the existing database
DATABASE_URL = get_required_env("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def get_db():
    """Yields a database session."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Creates the database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)
