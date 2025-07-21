from app.schemas.product_category import ProductCategoryResponse
from pydantic import BaseModel, Field
from typing import List, Optional


class ProductBase(BaseModel):
    """
    Base schema for products.
    - Defines common fields for all product schemas.
    - `sku`: Validated with regex to allow only uppercase letters and numbers.
    """

    sku: str = Field(..., min_length=3, max_length=20, pattern="^[A-Z0-9]+$")
    short_name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category_id: int = Field(..., gt=0)


class ProductCreate(ProductBase):
    """
    Schema for creating a product.
    - `active` is not included as it defaults to `True`.
    """

    pass


class ProductUpdate(BaseModel):
    """
    Schema for updating a product.
    - Allows updating `sku`, `short_name`, `description`, `category`, and `is_active`.
    """

    sku: Optional[str] = Field(None, min_length=3, max_length=20, pattern="^[A-Z0-9]+$")
    short_name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """
    Schema for product responses.
    - Includes `id` and `is_active`, which are generated in the database.
    """

    category_name: str = Field(..., min_length=3, max_length=50)
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class PaginatedProductResponse(BaseModel):
    data: List[ProductResponse]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}


class BulkStatusUpdateRequest(BaseModel):
    ids: list[int]
    is_active: bool
