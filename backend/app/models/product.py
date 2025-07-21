from typing import Optional
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    __tablename__ = "product"

    id: int = Field(default=None, primary_key=True, nullable=False)
    sku: str = Field(unique=True, index=True, nullable=False, description="Product SKU")
    short_name: str = Field(nullable=False, description="Short name of the product")
    description: Optional[str] = Field(default=None, description="Product description (optional)")
    category_id: int = Field(foreign_key="product_category.id", nullable=False, description="Category ID")
    is_active: bool = Field(default=True, nullable=False, description="Whether the product is active")
