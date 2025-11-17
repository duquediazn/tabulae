from app.utils.validation import normalize_category
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
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
def list_categories(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Lists all categories."""

    try:
        statement = select(ProductCategory).order_by(ProductCategory.name)
        categories = db.exec(statement.limit(limit).offset(offset)).all()
        total = db.exec(select(func.count()).select_from(ProductCategory)).first()
    except SQLAlchemyError:
        raise HTTPException(500, detail="Error retrieving product categories")
    return {"data": categories, "total": total, "limit": limit, "offset": offset}


@router.post("/", response_model=ProductCategoryResponse, status_code=201)
def create_category(
    data: ProductCategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Creates a category (only admins)."""
    category = ProductCategory(name=normalize_category(data.name))

    try:
        db.add(category)
        db.flush()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="A category with that name already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, detail="Internal error while creating category")

    return category


@router.put("/{id}", response_model=ProductCategoryResponse)
def update_category(
    id: int,
    data: ProductCategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Updates a category (only admins)."""
    category = db.get(ProductCategory, id)
    if not category:
        raise HTTPException(404, detail="Category not found")

    if data.name:
        category.name = normalize_category(data.name)

    try:
        db.add(category)
        db.flush()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Another category with that name already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, detail="Error updating category")

    return category


@router.delete("/{id}", response_model=ProductCategoryResponse)
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Deletes a category with no associated products (only admins)."""
    category = db.get(ProductCategory, id)
    if not category:
        raise HTTPException(404, detail="Category not found")

    # Check for associated products
    products = db.exec(select(Product).where(Product.category_id == id)).first()
    if products:
        raise HTTPException(
            400,
            detail="This category cannot be deleted because it has associated products",
        )

    try:
        db.delete(category)
        db.flush()
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, detail="Error deleting category")

    return category
