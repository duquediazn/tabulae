from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.dependencies import require_admin
from app.models.database import get_db
from app.models.stock_move_line import StockMoveLine
from app.models.stock import Stock
from app.models.warehouse import Warehouse
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.warehouse import (
    PaginatedWarehouseResponse,
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse
)
from app.schemas.common import BulkStatusUpdate, BulkStatusUpdateResponse

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("/", response_model=PaginatedWarehouseResponse)
async def get_warehouses(
    db: AsyncSession = Depends(get_db),
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
                func.lower(Warehouse.name).ilike(search_like)
            )

        if is_active is not None:
            statement = statement.where(Warehouse.is_active == is_active)

        paginated = (
            statement.order_by(Warehouse.name).limit(limit).offset(offset)
        )
        warehouses_result = await db.execute(paginated)
        warehouses = warehouses_result.scalars().all()
        total_result = await db.execute(
            select(func.count()).select_from(statement.subquery())
        )
        total_records = total_result.scalars().first() or 0

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


@router.put("/bulk-active", status_code=status.HTTP_200_OK, response_model=BulkStatusUpdateResponse)
async def bulk_update_is_active_warehouses(
    data: BulkStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        wh_result = await db.execute(select(Warehouse).where(Warehouse.id.in_(data.ids)))
        warehouses = wh_result.scalars().all()

        updated = []

        for warehouse in warehouses:
            if warehouse.is_active == data.is_active:
                continue

            if data.is_active is False:
                stock_result = await db.execute(
                    select(func.sum(Stock.quantity)).where(
                        Stock.warehouse_id == warehouse.id
                    )
                )
                stock_total = stock_result.scalars().first() or 0

                if stock_total > 0:
                    continue  # The warehouse still has products inside

            warehouse.is_active = data.is_active
            db.add(warehouse)
            updated.append(warehouse)

        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating warehouses")

    return {
        "message": f"{len(updated)} warehouses updated",
        "skipped": len(data.ids) - len(updated),
    }


@router.get("/{id}", response_model=WarehouseResponse)
async def get_warehouse(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves a specific warehouse by its ID. Admins can view inactive warehouses."""
    try:
        warehouse = await db.get(Warehouse, id)
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

    if current_user.role.strip().lower() != "admin" and not warehouse.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This warehouse is inactive.",
        )

    return warehouse


@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin), 
):
    """Creates a new warehouse. Only administrators are allowed."""
    new_warehouse = Warehouse(**warehouse_data.model_dump())

    try:
        db.add(new_warehouse)
        await db.commit()
        await db.refresh(new_warehouse)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error in the database.",
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while registering the warehouse.",
        )
    return new_warehouse


@router.put("/{id}", response_model=WarehouseResponse)
async def update_warehouse(
    id: int,
    warehouse_update: WarehouseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin), 
):
    """Edit the description or is_active status of a warehouse. Admins only."""
    try:
        warehouse = await db.get(Warehouse, id)
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
            stock_result = await db.execute(select(Stock).where(Stock.warehouse_id == id))
            stock = stock_result.scalars().first()
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
    if warehouse_update.name is not None:
        warehouse.name = warehouse_update.name
    if warehouse_update.is_active is not None:
        warehouse.is_active = warehouse_update.is_active

    try:
        db.add(warehouse)
        await db.commit()
        await db.refresh(warehouse)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error in the database.",
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating the warehouse.",
        )
    return warehouse


@router.delete("/{id}", response_model=WarehouseResponse)
async def deactivate_warehouse(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Deletes a warehouse only if it has no associated movements.
    The warehouse must be inactive and empty before deletion.
    Only administrators can perform this action.
    """
    try:
        warehouse = await db.get(Warehouse, id)
        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found"
            )

        if warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse must be inactive before it can be deleted"
            )
        
        stock_r = await db.execute(
            select(1)
            .where(Stock.warehouse_id == id)
            .limit(1)
        )
        stock = stock_r.scalars().first()

        if stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Warehouse {id} is not empty and therefore cannot be deleted.",
            )

        movement_r = await db.execute(
            select(1)
            .where(StockMoveLine.warehouse_id == id)
            .limit(1)
        )
        movement_exists = movement_r.scalars().first()

        if movement_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete this warehouse because it has registered movements."
            )
            
        await db.delete(warehouse)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error in the database."
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting the warehouse."
        )

    return warehouse
