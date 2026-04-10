from typing import Optional
from app.models.product_category import ProductCategory
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.dependencies import require_admin
from app.models.database import get_db
from app.models.product import Product
from app.models.stock import Stock
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.product import (
    BulkStatusUpdateRequest,
    PaginatedProductResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=PaginatedProductResponse)
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """Returns a paginated list of products.
    - An **admin** can see all products (active and inactive).
    - A **regular user** only sees active products.
    """
    try:
        statement = select(Product, ProductCategory.name).join(
            ProductCategory, Product.category_id == ProductCategory.id
        )

        if search:
            # Filter by short_name or sku (case-insensitive)
            search_like = f"%{search.lower()}%"
            statement = statement.where(
                func.lower(Product.short_name).ilike(search_like)
                | func.lower(Product.sku).ilike(search_like)
            )

        # Filter by category
        if category_id:
            statement = statement.where(Product.category_id == int(category_id))

        # Filter by active state (only admin can see inactive products)
        user_is_admin = current_user.role.strip().lower() == "admin"
        if not user_is_admin:
            statement = statement.where(Product.is_active == True)
        elif is_active is not None:
            statement = statement.where(Product.is_active == is_active)

        # Paginated and ordered query
        products_raw = db.exec(
            statement.order_by(Product.short_name).limit(limit).offset(offset)
        ).all()

        # Total count (without pagination)
        total_records = (
            db.exec(select(func.count()).select_from(statement.subquery())).first() or 0
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    products = [
        {**product.model_dump(), "category_name": category_name}
        for product, category_name in products_raw
    ]

    return {
        "data": products,
        "total": total_records,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{id}", response_model=ProductResponse)
def get_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a specific product by ID.
    - Regular users can only see active products.
    - Admins can see any product.
    """
    try:
        statement = (
            select(Product, ProductCategory.name)
            .join(ProductCategory, Product.category_id == ProductCategory.id)
            .where(Product.id == id)
        )
        result = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product, category_name = result

    if current_user.role.strip().lower() != "admin" and not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this product",
        )

    return {
        **product.model_dump(),
        "category_name": category_name,
    }

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),  
):
    """Creates a new product (admin only)."""

    # Check if the SKU already exists
    try:
        statement = select(Product).where(Product.sku == product_data.sku)
        existing_product = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU is already registered.",
        )

    category = db.get(ProductCategory, product_data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified category does not exist.",
        )

    # Create product
    new_product = Product(
        sku=product_data.sku,
        short_name=product_data.short_name,
        description=product_data.description,
        category_id=product_data.category_id,
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Please check the submitted data.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while creating the product.",
        )

    return {**new_product.model_dump(), "category_name": category.name}


@router.put("/bulk-status", status_code=status.HTTP_200_OK)
def bulk_update_product_status(
    data: BulkStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        rows = db.exec( 
            select(
                Product,
                func.coalesce(func.sum(Stock.quantity), 0).label("stock_total")
            )
            .join(Stock, Stock.product_id == Product.id, isouter=True)
            .where(Product.id.in_(data.ids))
            .group_by(Product.id)
        ).all()

        updated_products = []

        for product, stock_total in rows:
            if product.is_active == data.is_active:
                continue

            if data.is_active is False and stock_total > 0:
                continue  # Product still has stock, cannot be deactivated

            product.is_active = data.is_active
            db.add(product)
            updated_products.append(product)

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating products")

    return {
        "message": f"{len(updated_products)} products updated",
        "skipped": len(data.ids) - len(updated_products),
    }


@router.put("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Allows updating a product. Only admin users can update products."""

    try:
        # Search for the product in the database
        product = db.exec(
            select(Product)
            .where(Product.id == id)
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        
        # Validate if the new SKU already exists in another product
        if product_update.sku is not None and product_update.sku != product.sku:
            existing_product = db.exec(
                select(Product)
                .where(Product.sku == product_update.sku, Product.id != id)
            ).first()
            
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU is already in use",
                )    
            
        # Validate category and obtain category name (we need the name in the response as well)
        category_id = product_update.category_id if product_update.category_id is not None else product.category_id

        # Load the category from the database
        category = db.get(ProductCategory, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The specified category does not exist.")


        # If the active state is being updated, validate if the product can be deactivated
        if product_update.is_active is not None:
            if product_update.is_active is False:
                stock_total = (
                    db.exec(
                        select(func.sum(Stock.quantity)).where(
                            Stock.product_id == id
                        )
                    ).first()
                    or 0
                )
                
                if stock_total > 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This product still has remaining stock and cannot be deactivated.",
                    )  
        
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )         

    # sqlmodel_update will only update the fields that are set in the product_update object
    product.sqlmodel_update(product_update.model_dump(exclude_unset=True)) 

    try:
        # Save changes to the database
        db.add(product)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Please check the submitted data.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while updating the product.",
        )
    
    response = ProductResponse(
        sku=product.sku,
        short_name=product.short_name,
        description=product.description,
        category_id=product.category_id,
        category_name=category.name,
        id=product.id,
        is_active=product.is_active  
    )

    return response


@router.delete("/{id}", response_model=ProductResponse)
def delete_product(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """Allows an admin to delete a product."""

    try:
        statement = select(Product).where(Product.id == id)
        product = db.exec(statement).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        category = db.get(ProductCategory, product.category_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    try:
        db.delete(product)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This product has associated movements and cannot be deleted.")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")

    return {**product.model_dump(), "category_name": category.name}
