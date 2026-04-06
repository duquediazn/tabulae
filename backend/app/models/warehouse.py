from sqlmodel import SQLModel, Field

class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouse"

    id: int = Field(default=None, primary_key=True, nullable=False, description="Unique identifier for the warehouse")
    description: str = Field(nullable=False, max_length=255, description="Warehouse description")
    is_active: bool = Field(default=True, nullable=False, description="Whether the warehouse is active")
