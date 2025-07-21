from typing import List, Optional
from pydantic import BaseModel, Field
import datetime


class StockBase(BaseModel):
    """Base schema with common fields for stock."""

    warehouse_id: int = Field(..., description="Associated warehouse ID")
    warehouse_name: str = Field(..., description="Associated warehouse name")
    product_id: int = Field(..., description="Associated product ID")
    product_name: str = Field(..., description="Associated product name")
    sku: str = Field(..., min_length=3, max_length=20, pattern="^[A-Z0-9]+$")
    lot: str = Field(default="NO_LOT", description="Product lot identifier")
    expiration_date: Optional[datetime.date] = Field(
        default=None, description="Lot expiration date (if applicable)"
    )
    quantity: int = Field(..., ge=0, description="Available stock quantity")


class StockResponse(StockBase):
    """Schema for returning stock details."""

    class Config:
        from_attributes = True


class StockSummary(BaseModel):
    """Stock summary for a specific product or warehouse."""

    product_id: int = Field(..., description="Product ID")
    warehouse_id: int = Field(..., description="Warehouse ID")
    warehouse_name: str = Field(..., description="Warehouse name")
    total_quantity: int = Field(..., ge=0, description="Total stock for the product")


class StockHistory(BaseModel):
    """Schema for retrieving stock movement history."""

    move_id: int = Field(..., description="Movement ID")
    created_at: datetime.datetime = Field(..., description="Movement timestamp")
    move_type: str = Field(..., description="Movement move_type: 'incoming' or 'outgoing'")
    warehouse_id: int = Field(..., description="Involved warehouse ID")
    product_id: int = Field(..., description="Involved product ID")
    sku: str = Field(..., min_length=3, max_length=20, pattern="^[A-Z0-9]+$")
    lot: str = Field(
        default="NO_LOT",
        max_length=50,
        description="Product lot in the movement",
    )
    quantity: int = Field(..., ge=1, description="Quantity moved")
    user_name: str = Field(..., description="User who performed the movement")

    model_config = {"from_attributes": True}


class PaginatedStockResponse(BaseModel):
    """Pagination schema for StockResponse."""

    data: List[StockResponse]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}


class PaginatedStockSummary(BaseModel):
    """Pagination schema for StockSummary."""

    data: List[StockSummary]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}


class PaginatedStockHistory(BaseModel):
    """Pagination schema for StockHistory."""

    data: List[StockHistory]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}


class StockSemaphore(BaseModel):
    """Schema for stock expiration traffic light endpoint."""

    no_expiration: int = Field(
        ..., ge=0, description="No expiration or expires in more than 6 months"
    )
    expiring_soon: int = Field(
        ..., ge=0, description="Expires within the next 6 months"
    )
    expiring_now: int = Field(..., ge=0, description="Expires within the next month")

    model_config = {"from_attributes": True}


class StockByWarehouse(BaseModel):
    """Total stock grouped by warehouse (for bar chart)."""

    warehouse_id: int
    warehouse_name: str
    total_quantity: int

    model_config = {"from_attributes": True}


class StockByWarehousePieChart(BaseModel):
    """Stock quantity per product in a specific warehouse (for pie chart)."""

    product_id: int
    product_name: str
    total_quantity: int


class StockByCategory(BaseModel):
    category_id: int
    category_name: str
    total_quantity: int

    model_config = {"from_attributes": True}


class StockByProductInCategory(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int

    model_config = {"from_attributes": True}


class AvailableLotResponse(BaseModel):
    lot: str
    expiration_date: Optional[datetime.date]
    quantity: int
