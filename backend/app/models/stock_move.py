from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class StockMove(SQLModel, table=True):
    __tablename__ = "stock_move"

    move_id: int = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    move_type: str = Field(
        nullable=False
    )  # Movement type as a string; constraint is handled in the schema
    user_id: int = Field(foreign_key="user.id", nullable=False)
