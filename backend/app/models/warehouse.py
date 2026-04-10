from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String

class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouse"

    id: int = Field(default=None, primary_key=True, nullable=False, description="Unique identifier for the warehouse")
    name: str = Field(sa_column=Column("name", String(255), nullable=False), description="Warehouse name")
    is_active: bool = Field(default=True, nullable=False, description="Whether the warehouse is active")


