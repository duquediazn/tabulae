from sqlmodel import Column, SQLModel, Field, String

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(nullable=False, description="User's full name")
    email: str = Field(unique=True, nullable=False, index=True, description="User email")
    password: str = Field(nullable=False, description="Hashed password")
    role: str = Field(nullable=False, description="User role: 'admin' or 'user'")
    is_active: bool = Field(default=True, nullable=False, description="Whether the user is active")
