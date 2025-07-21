import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Stock(SQLModel, table=True):
    """SQLModel to represent stock levels in warehouses."""

    __tablename__ = "stock"

    warehouse_id: int = Field(
        foreign_key="warehouse.id",
        primary_key=True,
        description="ID of the associated warehouse",
    )
    product_id: int = Field(
        foreign_key="product.id",
        primary_key=True,
        description="ID of the associated product",
    )
    lot: str = Field(
        primary_key=True,
        default="NO_LOT",
        description="Lot identifier of the product",
    )
    expiration_date: Optional[datetime.date] = Field(
        default=None, description="Expiration date (if applicable)"
    )
    quantity: int = Field(
        nullable=False, ge=0, description="Quantity in stock (minimum 0)"
    )
