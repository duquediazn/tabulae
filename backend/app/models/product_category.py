from sqlmodel import SQLModel, Field

class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_category"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True, description="Category name")
