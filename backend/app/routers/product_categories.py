from app.utils.validation import normalize_category
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies import get_current_user
from app.models.user import User
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional

from app.models.database import get_db
from app.models.product_category import ProductCategory
from app.models.product import Product
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCategoryResponse,
    PaginatedProductCategoryResponse,
)
from app.dependencies import require_admin

router = APIRouter(prefix="/categories", tags=["Product Categories"])


@router.get("/", response_model=PaginatedProductCategoryResponse)
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Lists all categories."""

    try:
        statement = select(ProductCategory).order_by(ProductCategory.name)
        total_result = await db.execute(select(func.count()).select_from(statement.subquery()))
        total = total_result.scalars().first() or 0
        categories_result = await db.execute(statement.limit(limit).offset(offset))
        categories = categories_result.scalars().all()
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving product categories")
    return {"data": categories, "total": total, "limit": limit, "offset": offset}


@router.post("/", response_model=ProductCategoryResponse, status_code=201)
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Creates a category (only admins)."""
    category = ProductCategory(name=normalize_category(data.name))

    try:
        db.add(category)
        await db.commit()
        await db.refresh(category)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A category with that name already exists")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error while creating category")

    return category


@router.put("/{id}", response_model=ProductCategoryResponse)
async def update_category(
    id: int,
    data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Updates a category (only admins)."""
    try:
        category = await db.get(ProductCategory, id)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating category")
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if data.name:
        category.name = normalize_category(data.name)

    try:
        db.add(category)
        await db.commit()
        await db.refresh(category)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Another category with that name already exists")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating category")

    return category


@router.delete("/{id}", response_model=ProductCategoryResponse)
async def delete_category(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deletes a category with no associated products (only admins)."""
    try:
        category = await db.get(ProductCategory, id)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting category")
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Check for associated products
    products_result = await db.execute(select(Product).where(Product.category_id == id))
    products = products_result.scalars().first()
    if products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This category cannot be deleted because it has associated products",
        )

    try:
        await db.delete(category)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting category")

    return category
