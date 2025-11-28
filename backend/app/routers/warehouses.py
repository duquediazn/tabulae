from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.dependencies import require_admin
from app.models import user
from app.models.database import get_db
from app.models.stock_move_line import StockMoveLine
from app.models.stock import Stock
from app.models.warehouse import Warehouse
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.warehouse import (
    PaginatedWarehouseResponse,
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    BulkStatusUpdate,
)
from app.utils.validation import is_admin_user

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("/", response_model=PaginatedWarehouseResponse)
def get_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """Lists all warehouses. Both regular users and admins can view them."""
    try:
        statement = select(Warehouse)

        if search:
            search_like = f"%{search.lower()}%"
            statement = statement.where(
                func.lower(Warehouse.description).ilike(search_like)
            )

        if is_active is not None:
            statement = statement.where(Warehouse.is_active == is_active)

        paginated = (
            statement.order_by(Warehouse.description).limit(limit).offset(offset)
        )
        warehouses = db.exec(paginated).all()

        total_records = (
            db.exec(select(func.count()).select_from(statement.subquery())).first() or 0
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
    return {
        "data": warehouses,
        "total": total_records,
        "limit": limit,
        "offset": offset,
    }


@router.put("/bulk-active", status_code=200)
def bulk_update_is_active_warehouses(
    data: BulkStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        warehouses = db.exec(select(Warehouse).where(Warehouse.id.in_(data.ids))).all()

        updated = []

        for warehouse in warehouses:
            if warehouse.is_active == data.is_active:
                continue

            if data.is_active is False:
                stock_total = (
                    db.exec(
                        select(func.sum(Stock.quantity)).where(
                            Stock.warehouse_id == warehouse.id
                        )
                    ).first()
                    or 0
                )

                if stock_total > 0:
                    continue  # The warehouse still has products inside

            warehouse.is_active = data.is_active
            db.add(warehouse)
            updated.append(warehouse)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, detail="Error updating warehouses")

    db.commit()
    return {
        "message": f"{len(updated)} warehouses updated",
        "skipped": len(data.ids) - len(updated),
    }


@router.get("/{id}", response_model=WarehouseResponse)
def get_warehouse(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves a specific warehouse by its ID. Admins can view inactive warehouses."""
    try:
        warehouse = db.get(Warehouse, id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    if not is_admin_user(current_user) and not warehouse.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This warehouse is inactive.",
        )

    return warehouse


@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),  # Only admins can create
):
    """Creates a new warehouse. Only administrators are allowed."""
    new_warehouse = Warehouse(**warehouse_data.model_dump())

    try:
        db.add(new_warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error in the database.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while registering the warehouse.",
        )
    db.commit()
    db.refresh(new_warehouse)
    return new_warehouse


@router.put("/{id}", response_model=WarehouseResponse)
def update_warehouse(
    id: int,
    warehouse_update: WarehouseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),  # Only admins can modify
):
    """Edit the description or is_active status of a warehouse. Admins only."""
    try:
        warehouse = db.get(Warehouse, id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
        )

    if warehouse_update.is_active is False:
        try:
            stock = db.exec(select(Stock).where(Stock.warehouse_id == id)).first()
            if stock:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Warehouse {id} is not empty and therefore cannot be deactivated.",
                )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error",
            )

    # Update only provided fields
    if warehouse_update.description:
        warehouse.description = warehouse_update.description
    if warehouse_update.is_active is not None:
        warehouse.is_active = warehouse_update.is_active

    try:
        db.add(warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error in the database.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating the warehouse.",
        )
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete("/{id}", response_model=WarehouseResponse)
def deactivate_warehouse(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Deletes a warehouse only if it has no associated movements.
    Only administrators can perform this action.
    """
    try:
        warehouse = db.get(Warehouse, id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found"
        )

    try:
        movement_exists = db.exec(
            select(StockMoveLine).where(StockMoveLine.warehouse_id == id)
        ).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if movement_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete this warehouse because it has registered movements.",
        )

    try:
        db.delete(warehouse)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error in the database.",
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while deleting the warehouse. Error: {e}",
        )
    db.commit()

    return warehouse
