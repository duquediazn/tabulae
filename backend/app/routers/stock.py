from datetime import datetime, timezone
from typing import List
from dateutil.relativedelta import relativedelta
from app.models.product_category import ProductCategory
from app.models.warehouse import Warehouse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, case, func, select
from sqlalchemy.exc import SQLAlchemyError
from app.models.database import get_db
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.product import Product
from app.models.stock import Stock
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.stock import (
    AvailableLotResponse,
    PaginatedStockHistory,
    PaginatedStockResponse,
    PaginatedStockSummary,
    StockByCategory,
    StockByProductInCategory,
    StockByWarehouse,
    StockByWarehousePieChart,
    StockResponse,
    StockSemaphore,
    StockSummary,
    StockHistory,
)

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("/", response_model=PaginatedStockResponse)
def get_all_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Lists all stock across all warehouses."""
    try:
        statement = (
            select(
                Stock.warehouse_id,
                Warehouse.description,
                Stock.product_id,
                Product.short_name,
                Product.sku,
                Stock.lot,
                Stock.expiration_date,
                Stock.quantity,
            )
            .order_by(Stock.warehouse_id, Stock.product_id, Stock.lot)
            .limit(limit)
            .offset(offset)
        )
        stock = db.exec(statement).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockResponse(
        data=[
            StockResponse(
                warehouse_id=item.warehouse_id,
                warehouse_name=item.description,
                product_id=item.product_id,
                product_name=item.short_name,
                sku=item.sku,
                lot=item.lot,
                expiration_date=item.expiration_date,
                quantity=item.quantity,
            )
            for item in stock
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/warehouse/{warehouse_id}", response_model=PaginatedStockResponse)
def get_stock_by_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Lists the stock of a specific warehouse."""
    try:
        statement = (
            select(
                Stock.warehouse_id,
                Warehouse.description,
                Stock.product_id,
                Product.short_name,
                Product.sku,
                Stock.lot,
                Stock.expiration_date,
                Stock.quantity,
            )
            .join(Warehouse, Warehouse.id == Stock.warehouse_id)
            .join(Product, Product.id == Stock.product_id)
            .where(Stock.warehouse_id == warehouse_id)
            .order_by(Stock.warehouse_id, Stock.product_id, Stock.lot)
            .limit(limit)
            .offset(offset)
        )
        stock = db.exec(statement).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
    return PaginatedStockResponse(
        data=[
            StockResponse(
                warehouse_id=item.warehouse_id,
                warehouse_name=item.description,
                product_id=item.product_id,
                product_name=item.short_name,
                sku=item.sku,
                lot=item.lot,
                expiration_date=item.expiration_date,
                quantity=item.quantity,
            )
            for item in stock
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/warehouse/{warehouse_id}/detail", response_model=List[StockByWarehousePieChart]
)
def get_stock_by_warehouse_pie_chart(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Total stock quantity per product in a specific warehouse."""
    try:
        statement = (
            select(
                Stock.product_id,
                Product.short_name,
                func.sum(Stock.quantity).label("total_quantity"),
            )
            .join(Product, Product.id == Stock.product_id)
            .where(Stock.warehouse_id == warehouse_id)
            .group_by(Stock.product_id, Product.short_name)
        )
        stock = db.exec(statement).all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return [
        StockByWarehousePieChart(
            product_id=row.product_id,
            product_name=row.short_name,
            total_quantity=row.total_quantity,
        )
        for row in stock
    ]


@router.get(
    "/product/expiring",
    response_model=PaginatedStockResponse,
)
def get_stock_by_product_expiration_date(
    from_months: int = Query(
        0, ge=0, description="Start of the expiration window in months from today"
    ),
    range_months: int = Query(
        1, ge=1, description="Duration of the expiration window in months"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns total stock of products expiring within a given date range (relative to today)."""

    try:
        today_utc = datetime.now(timezone.utc).date()
        start_date = today_utc + relativedelta(months=from_months)
        end_date = start_date + relativedelta(months=range_months)

        statement = (
            select(
                Stock.warehouse_id,
                Warehouse.description,
                Stock.product_id,
                Product.short_name,
                Product.sku,
                Stock.lot,
                Stock.expiration_date,
                Stock.quantity,
            )
            .join(Warehouse, Warehouse.id == Stock.warehouse_id)
            .join(Product, Product.id == Stock.product_id)
            .where(
                Stock.expiration_date > start_date,
                Stock.expiration_date <= end_date,
                Stock.quantity > 0,
            )
        )

        stock = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockResponse(
        data=[
            StockResponse(
                warehouse_id=item.warehouse_id,
                warehouse_name=item.description,
                product_id=item.product_id,
                product_name=item.short_name,
                sku=item.sku,
                lot=item.lot,
                expiration_date=item.expiration_date,
                quantity=item.quantity,
            )
            for item in stock
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/product/{product_id}",
    response_model=PaginatedStockSummary,
)
def get_stock_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns the total stock of a product across all warehouses."""

    try:
        statement = (
            select(
                Stock.product_id,
                Stock.warehouse_id,
                Warehouse.description.label("warehouse_name"),
                func.sum(Stock.quantity).label("total_quantity"),
            )
            .join(Warehouse, Warehouse.id == Stock.warehouse_id)
            .where(Stock.product_id == product_id)
            .group_by(Stock.product_id, Stock.warehouse_id, Warehouse.description)
        )

        stock_summary = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockSummary(
        data=[
            StockSummary(
                product_id=item.product_id,
                warehouse_id=item.warehouse_id,
                warehouse_name=item.warehouse_name,
                total_quantity=item.total_quantity,
            )
            for item in stock_summary
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/warehouse/{warehouse_id}/product/{product_id}",
    response_model=PaginatedStockResponse,
)
def get_stock_by_warehouse_and_product(
    warehouse_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns the stock of a product in a specific warehouse."""

    try:
        statement = (
            select(
                Stock.warehouse_id,
                Warehouse.description,
                Stock.product_id,
                Product.short_name,
                Product.sku,
                Stock.lot,
                Stock.expiration_date,
                Stock.quantity,
            )
            .join(Warehouse, Warehouse.id == Stock.warehouse_id)
            .join(Product, Product.id == Stock.product_id)
            .where(
                Stock.warehouse_id == warehouse_id,
                Stock.product_id == product_id,
            )
        )
        stock = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockResponse(
        data=[
            StockResponse(
                warehouse_id=item.warehouse_id,
                warehouse_name=item.description,
                product_id=item.product_id,
                product_name=item.short_name,
                sku=item.sku,
                lot=item.lot,
                expiration_date=item.expiration_date,
                quantity=item.quantity,
            )
            for item in stock
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/history", response_model=PaginatedStockHistory)
def get_stock_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns the stock movement history (all movement lines)."""
    try:
        statement = (
            select(
                StockMove.move_id,
                StockMove.created_at,
                StockMove.move_type,
                StockMoveLine.warehouse_id,
                StockMoveLine.product_id,
                Product.sku,
                StockMoveLine.lot,
                StockMoveLine.quantity,
                User.name.label("user_name"),
            )
            .join(StockMoveLine, StockMove.move_id == StockMoveLine.move_id)
            .join(User, StockMove.user_id == User.id)
            .join(Product, Product.id == StockMoveLine.product_id)
            .order_by(StockMove.created_at.desc())
        )
        history = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockHistory(
        data=[
            StockHistory(
                move_id=item.move_id,
                created_at=item.created_at,
                move_type=item.move_type,
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
                sku=item.sku,
                lot=item.lot,
                quantity=item.quantity,
                user_name=item.user_name,
            )
            for item in history
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/product/{product_id}/history", response_model=PaginatedStockHistory)
def get_product_stock_history(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns the stock movement history for a specific product."""
    try:
        statement = (
            select(
                StockMove.move_id,
                StockMove.created_at,
                StockMove.move_type,
                StockMoveLine.warehouse_id,
                StockMoveLine.product_id,
                Product.sku,
                StockMoveLine.lot,
                StockMoveLine.quantity,
                User.name.label("user_name"),
            )
            .join(StockMoveLine, StockMove.move_id == StockMoveLine.move_id)
            .join(User, StockMove.user_id == User.id)
            .join(Product, Product.id == StockMoveLine.product_id)
            .where(Product.id == product_id)
            .order_by(StockMove.created_at.desc(), StockMoveLine.lot)
        )
        history = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockHistory(
        data=[
            StockHistory(
                move_id=item.move_id,
                created_at=item.created_at,
                move_type=item.move_type,
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
                sku=item.sku,
                lot=item.lot,
                quantity=item.quantity,
                user_name=item.user_name,
            )
            for item in history
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/warehouse/{warehouse_id}/history", response_model=PaginatedStockHistory)
def get_warehouse_stock_history(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns the stock movement history for a specific warehouse."""
    try:
        statement = (
            select(
                StockMove.move_id,
                StockMove.created_at,
                StockMove.move_type,
                StockMoveLine.warehouse_id,
                StockMoveLine.product_id,
                Product.sku,
                StockMoveLine.lot,
                StockMoveLine.quantity,
                User.name.label("user_name"),
            )
            .join(StockMoveLine, StockMove.move_id == StockMoveLine.move_id)
            .join(User, StockMove.user_id == User.id)
            .join(Product, Product.id == StockMoveLine.product_id)
            .where(StockMoveLine.warehouse_id == warehouse_id)
            .order_by(StockMove.created_at.desc(), StockMoveLine.lot)
        )
        history = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockHistory(
        data=[
            StockHistory(
                move_id=item.move_id,
                created_at=item.created_at,
                move_type=item.move_type,
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
                sku=item.sku,
                lot=item.lot,
                quantity=item.quantity,
                user_name=item.user_name,
            )
            for item in history
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/warehouse/{warehouse_id}/product/{product_id}/history",
    response_model=PaginatedStockHistory,
)
def get_warehouse_and_product_stock_history(
    product_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Returns the stock movement history filtered by warehouse and product."""
    try:
        statement = (
            select(
                StockMove.move_id,
                StockMove.created_at,
                StockMove.move_type,
                StockMoveLine.warehouse_id,
                StockMoveLine.product_id,
                Product.sku,
                StockMoveLine.lot,
                StockMoveLine.quantity,
                User.name.label("user_name"),
            )
            .join(StockMoveLine, StockMove.move_id == StockMoveLine.move_id)
            .join(User, StockMove.user_id == User.id)
            .join(Product, Product.id == StockMoveLine.product_id)
            .where(
                Product.id == product_id,
                StockMoveLine.warehouse_id == warehouse_id,
            )
            .order_by(StockMove.created_at.desc(), StockMoveLine.lot)
        )
        history = db.exec(statement.limit(limit).offset(offset)).all()
        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return PaginatedStockHistory(
        data=[
            StockHistory(
                move_id=item.move_id,
                created_at=item.created_at,
                move_type=item.move_type,
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
                sku=item.sku,
                lot=item.lot,
                quantity=item.quantity,
                user_name=item.user_name,
            )
            for item in history
        ],
        total=total_records or 0,
        limit=limit,
        offset=offset,
    )


@router.get("/semaphore", response_model=StockSemaphore)
def get_stock_status_semaphore(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns stock status segmented by expiration (traffic light) — total units."""

    try:
        today = datetime.now(timezone.utc).date()
        in_1_month = today + relativedelta(months=1)
        in_6_months = today + relativedelta(months=6)

        expiring_now = (
            db.exec(
                select(func.sum(Stock.quantity)).where(
                    Stock.expiration_date != None,
                    Stock.expiration_date > today,
                    Stock.expiration_date <= in_1_month,
                )
            ).first()
            or 0
        )

        expiring_soon = (
            db.exec(
                select(func.sum(Stock.quantity)).where(
                    Stock.expiration_date > in_1_month,
                    Stock.expiration_date <= in_6_months,
                )
            ).first()
            or 0
        )

        no_expiration = (
            db.exec(
                select(func.sum(Stock.quantity)).where(
                    (Stock.expiration_date == None)
                    | (Stock.expiration_date > in_6_months)
                )
            ).first()
            or 0
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database connection error",
        )

    return {
        "expiring_now": expiring_now,
        "expiring_soon": expiring_soon,
        "no_expiration": no_expiration,
    }


@router.get("/warehouses/detail", response_model=List[StockByWarehouse])
def get_warehouse_stock_detail(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the total stock quantity of all products, grouped by warehouse."""
    try:
        statement = (
            select(
                Stock.warehouse_id,
                Warehouse.description,
                func.sum(Stock.quantity).label("total_quantity"),
            )
            .join(Warehouse, Warehouse.id == Stock.warehouse_id)
            .group_by(Stock.warehouse_id, Warehouse.id)
        )
        data = db.exec(statement).all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    result = [
        StockByWarehouse(
            warehouse_id=item.warehouse_id,
            warehouse_name=item.description,
            total_quantity=item.total_quantity,
        )
        for item in data
    ]

    return result


@router.get("/product-categories", response_model=List[StockByCategory])
def get_stock_by_product_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the total stock quantity grouped by product category.
    """
    try:
        statement = (
            select(
                ProductCategory.id,
                ProductCategory.name,
                func.sum(Stock.quantity).label("total_quantity"),
            )
            .join(Product, ProductCategory.id == Product.category_id)
            .join(Stock, Stock.product_id == Product.id)
            .group_by(ProductCategory.id, ProductCategory.name)
            .order_by(ProductCategory.name)
        )
        results = db.exec(statement).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Error retrieving stock by category",
        )

    return [
        StockByCategory(
            category_id=row.id,
            category_name=row.name,
            total_quantity=row.total_quantity,
        )
        for row in results
    ]


@router.get(
    "/category/{category_id}/products", response_model=List[StockByProductInCategory]
)
def get_stock_by_category_detail(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the total stock quantity per product within a specific category.
    """
    try:
        statement = (
            select(
                Product.id,
                Product.short_name,
                func.sum(Stock.quantity).label("total_quantity"),
            )
            .join(Stock, Stock.product_id == Product.id)
            .where(Product.category_id == category_id)
            .group_by(Product.id, Product.short_name)
            .order_by(Product.short_name)
        )
        results = db.exec(statement).all()
    except SQLAlchemyError:
        raise HTTPException(
            500,
            detail="Error retrieving stock data for products in the selected category.",
        )

    return [
        StockByProductInCategory(
            product_id=row.id,
            product_name=row.short_name,
            total_quantity=row.total_quantity,
        )
        for row in results
    ]


@router.get("/available-lots", response_model=list[AvailableLotResponse])
def get_lots_disponibles(
    product: int = Query(..., gt=0),
    warehouse: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the available lots for a given product in a warehouse.
    Only lots with a stock quantity greater than 0 are included.
    """

    try:
        statement = (
            select(
                Stock.lot,
                Stock.expiration_date,
                func.sum(Stock.quantity).label("quantity"),
            )
            .where(Stock.product_id == product)
            .where(Stock.warehouse_id == warehouse)
            .where(Stock.quantity > 0)
            .group_by(Stock.lot, Stock.expiration_date)
            .order_by(Stock.expiration_date)
        )

        results = db.exec(statement).all()

        return [
            AvailableLotResponse(
                lot=row.lot or "NO_LOT",
                expiration_date=row.expiration_date,
                quantity=row.quantity,
            )
            for row in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching available lots",
        )
