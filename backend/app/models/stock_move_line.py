from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class StockMoveLine(SQLModel, table=True):
    __tablename__ = "stock_move_line"

    move_id: int = Field(foreign_key="stock_move.move_id", primary_key=True)
    line_id: int = Field(primary_key=True, ge=1)  # Must be greater than 0
    warehouse_id: int = Field(foreign_key="warehouse.id", nullable=False)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    lot: str = Field(default="NO_LOT", max_length=50)
    expiration_date: Optional[date] = Field(default=None)
    quantity: int = Field(nullable=False, ge=1)  # Quantity must be greater than 0

