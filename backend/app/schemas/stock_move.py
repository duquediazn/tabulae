from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, List
from app.schemas.stock_move_line import StockMoveLineCreate, StockMoveLineResponse


class StockMoveBase(BaseModel):
    """Base schema with common fields for a movement."""

    move_type: Literal["incoming", "outgoing"] = Field(
        ..., description="Must be 'incoming' or 'outgoing'"
    )
    user_id: int = Field(..., description="ID of the user performing the movement")


class StockMoveCreate(StockMoveBase):
    """Schema for creating a movement.
    - Includes `lines` to register associated movement lines.
    """

    lines: List[StockMoveLineCreate] = Field(..., description="List of movement lines")


class StockMoveResponse(StockMoveBase):
    """Schema for returning movement data."""

    move_id: int
    created_at: datetime
    user_name: str
    lines: List[StockMoveLineResponse] = Field(
        default=[], description="StockMove lines"
    )

    class Config:
        from_attributes = True  # Enables automatic conversion from SQLModel to JSON


class PaginatedStockMovesResponse(BaseModel):
    data: List[StockMoveResponse]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True


class StockMoveSummary(BaseModel):
    move_type: str
    quantity: int

    class Config:
        from_attributes = True


class StockMoveLastYearGraph(BaseModel):
    move_id: int
    user_id: int
    created_at: datetime
    move_type: str
