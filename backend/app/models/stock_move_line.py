from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, CheckConstraint
from typing import Optional
from datetime import date

class StockMoveLine(SQLModel, table=True):
    __tablename__ = "stock_move_line"

    move_id: int = Field(foreign_key="stock_move.id", primary_key=True)
    line_id: int = Field(sa_column=Column(Integer, CheckConstraint("line_id > 0"), primary_key=True))
    warehouse_id: int = Field(foreign_key="warehouse.id", nullable=False,index=True)
    product_id: int = Field(foreign_key="product.id", nullable=False,index=True)
    lot: str = Field(default="NO_LOT", max_length=50)
    expiration_date: Optional[date] = Field(default=None)
    quantity: int = Field(sa_column=Column(Integer, CheckConstraint("quantity > 0"), nullable=False))

