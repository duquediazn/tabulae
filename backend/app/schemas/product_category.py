from pydantic import BaseModel, Field
from typing import List, Optional


class ProductCategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)


class ProductCategoryResponse(ProductCategoryBase):
    id: int

    model_config = {"from_attributes": True}


class PaginatedProductCategoryResponse(BaseModel):
    data: List[ProductCategoryResponse]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}
