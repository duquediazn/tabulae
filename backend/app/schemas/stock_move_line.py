from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class StockMoveLineBase(BaseModel):
    """Base schema for a movement line with common fields."""

    warehouse_id: int = Field(
        ..., description="Code of the warehouse where the movement takes place"
    )
    product_id: int = Field(..., description="Code of the product being moved")
    lot: Optional[str] = Field(
        default="NO_LOT", max_length=50, description="Product batch (optional)"
    )
    expiration_date: Optional[date] = Field(
        None, description="Product expiration date (optional)"
    )
    quantity: int = Field(
        ..., ge=1, description="Quantity of products moved (must be greater than 0)"
    )


class StockMoveLineCreate(StockMoveLineBase):
    """Schema for creating a movement line."""

    pass  # `id_mov` and `id_linea` are auto-generated


class StockMoveLineResponse(StockMoveLineBase):
    """Response schema with additional IDs."""

    move_id: int
    line_id: int

    class Config:
        from_attributes = True  # Allows converting SQLModel to JSON responses


class PaginatedStockMoveLineResponse(BaseModel):
    data: List[StockMoveLineResponse]
    total: int
    limit: int
    offset: int


class StockMoveLineWithNamesResponse(StockMoveLineResponse):
    product_name: str
    warehouse_name: str


class PaginatedStockMoveLineWithNamesResponse(BaseModel):
    data: List[StockMoveLineWithNamesResponse]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}
