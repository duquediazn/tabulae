import logging
from collections import defaultdict
from datetime import date, datetime, time, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, select, case, cast, DateTime
from dateutil.relativedelta import relativedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.stock_move import (
    StockMoveLastYearGraph,
    StockMoveResponse,
    StockMoveCreate,
    PaginatedStockMovesResponse,
    StockMoveSummary,
)
from app.dependencies import get_current_user
from app.schemas.stock_move_line import (
    StockMoveLineResponse,
    PaginatedStockMoveLineWithNamesResponse,
)
from app.routers.websocket import manager
from app.services.stock_move_service import create_stock_movement
import anyio

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/stock-movements", tags=["Stock Movements"])


@router.get("/", response_model=PaginatedStockMovesResponse)
async def get_movements(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    move_type: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    user_id: Optional[int] = Query(None),
):
    """List all stock movements. Admin sees all, regular users see only their own, including lines."""
    try:
        statement = select(StockMove, User.name).join(
            User, StockMove.user_id == User.id
        )

        if search:
            search_like = f"%{search.lower()}%"
            statement = statement.where(func.lower(User.name).ilike(search_like))

        if move_type in {"incoming", "outgoing"}:
            statement = statement.where(StockMove.move_type == move_type)

        if date_from:
            dt_from = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            statement = statement.where(StockMove.created_at >= dt_from)

        if date_to:
            dt_to = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
            statement = statement.where(StockMove.created_at <= dt_to)

        if user_id and current_user.role.strip().lower() == "admin":
            statement = statement.where(StockMove.user_id == user_id)

        if current_user.role.strip().lower() != "admin":
            statement = statement.where(StockMove.user_id == current_user.id)

        results = await db.execute(
            statement.order_by(StockMove.created_at.desc()).limit(limit).offset(offset)
        )
        results = results.all()

        total_records = (
            await db.execute(select(func.count()).select_from(statement.subquery()))
        )
        total_records = total_records.scalars().first() or 0
        
        # Extract movement ids from the results to fetch lines in a single query
        ids = [movement.id for movement, _ in results]
        
        # Fetch all lines for the retrieved movements in a single query
        all_lines = await db.execute(
            select(StockMoveLine).where(StockMoveLine.move_id.in_(ids))
        )
        all_lines = all_lines.scalars().all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
    
    # List to hold the final response objects
    movements_response = []

    # Group lines by move_id for easy association with movements
    lines_by_move = defaultdict(list) # defaultdict to automatically create a list for new keys
    for line in all_lines: 
        lines_by_move[line.move_id].append(line)

    for movement, user_name in results:
        movements_response.append(
            StockMoveResponse(
                id=movement.id,
                created_at=movement.created_at,
                move_type=movement.move_type,
                user_id=movement.user_id,
                user_name=user_name,
                lines=[
                    StockMoveLineResponse.model_validate(line)
                    for line in lines_by_move[movement.id]
                ],
            )
        )

    return {
        "data": movements_response,
        "total": total_records,
        "limit": limit,
        "offset": offset,
    }


@router.get("/last-year", response_model=List[StockMoveLastYearGraph])
async def get_movements_last_year(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns movements from the last year. Filters by user if not admin."""
    date_to = datetime.combine(datetime.now(timezone.utc).date(), time.max).replace(
        tzinfo=timezone.utc
    )
    date_from = date_to - relativedelta(years=1)

    try:
        month_trunc = cast(func.date_trunc("month", StockMove.created_at), DateTime)
        statement = (
            select(
                month_trunc.label("month"),
                func.count(case((StockMove.move_type == "incoming", 1))).label("incoming"),
                func.count(case((StockMove.move_type == "outgoing", 1))).label("outgoing"),
            )
            .where(StockMove.created_at >= date_from)
            .where(StockMove.created_at <= date_to)
            .group_by(month_trunc)
            .order_by(month_trunc)
        )

        if current_user.role.strip().lower() != "admin":
            statement = statement.where(StockMove.user_id == current_user.id)

        results = await db.execute(statement)
        results = results.all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return [
        StockMoveLastYearGraph(
            month=row.month,
            incoming=row.incoming,
            outgoing=row.outgoing,
        )
        for row in results
    ]


@router.get("/{id}", response_model=StockMoveResponse)
async def get_movement(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves the details of a specific movement along with its lines.
    - **Regular users** can only view their own movements.
    - **Admins** can view any movement.
    """
    try:
        statement = (
            select(StockMove, User.name)
            .join(User, StockMove.user_id == User.id)
            .where(StockMove.id == id)
)
        result = await db.execute(statement)
        result = result.first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movement not found"
        )

    movement, user_name = result

    # If not admin and the movement does not belong to the authenticated user, deny access
    if current_user.role.strip().lower() != "admin" and movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this movement.",
        )

    # Retrieve movement lines
    try:
        statement_lines = select(StockMoveLine).where(
            StockMoveLine.move_id == movement.id
        )
        movement_lines = await db.execute(statement_lines)
        movement_lines = movement_lines.scalars().all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving the movement lines.",
        )

    return StockMoveResponse(
        id=movement.id,
        created_at=movement.created_at,
        move_type=movement.move_type,
        user_id=movement.user_id,
        user_name=user_name or "Unknown",
        lines=[StockMoveLineResponse.model_validate(line) for line in movement_lines],
    )


@router.post("/", response_model=StockMoveResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    movement_data: StockMoveCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Registers a stock movement with all its lines in a single request.
    - If a product is inactive, the operation is interrupted.
    - If a warehouse is inactive, the operation is interrupted.
    """
    new_movement, created_lines = await create_stock_movement(movement_data, current_user.id, db)

    # Broadcast to connected WebSocket clients.
    try:
        message = f"New stock movement recorded: {new_movement.id} ({new_movement.move_type})"
        await manager.broadcast(message)
    except Exception as e:
        logger.warning("WebSocket broadcast failed: %s", str(e))

    return StockMoveResponse(
        id=new_movement.id,
        created_at=new_movement.created_at,
        move_type=new_movement.move_type,
        user_id=new_movement.user_id,
        user_name=current_user.name,
        lines=[StockMoveLineResponse.model_validate(line) for line in created_lines],
    )


@router.get("/{id}/lines", response_model=PaginatedStockMoveLineWithNamesResponse)
async def get_movement_lines(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Lists all lines of a movement with product and warehouse names."""

    try:
        statement = select(StockMove).where(StockMove.id == id)
        result = await db.execute(statement)
        movement = result.scalars().first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found",
        )

    if current_user.role.strip().lower() != "admin" and movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this movement",
        )

    try:
        statement_lines = (
            select(StockMoveLine, Product.short_name, Warehouse.name)
            .join(Product, Product.id == StockMoveLine.product_id)
            .join(Warehouse, Warehouse.id == StockMoveLine.warehouse_id)
            .where(StockMoveLine.move_id == id)
            .order_by(StockMoveLine.line_id)
        )

        result_lines = await db.execute(statement_lines.limit(limit).offset(offset))
        results = result_lines.all()
        total_records_result = await db.execute(
            select(func.count()).select_from(statement_lines.subquery())
        )
        total_records = total_records_result.scalar() or 0

        lines = []
        for line, product_name, warehouse_name in results:
            lines.append(
                {
                    "line_id": line.line_id,
                    "move_id": line.move_id,
                    "warehouse_id": line.warehouse_id,
                    "product_id": line.product_id,
                    "product_name": product_name,
                    "warehouse_name": warehouse_name,
                    "lot": line.lot,
                    "expiration_date": line.expiration_date,
                    "quantity": line.quantity,
                }
            )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading movement lines",
        )

    return {
        "data": lines,
        "total": total_records,
        "limit": limit,
        "offset": offset,
    }


@router.get("/summary/move-type", response_model=List[StockMoveSummary])
async def count_movements_by_move_type(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Counts the number of stock movements grouped by move type (incoming, outgoing)."""
    try:
        statement = select(StockMove.move_type, func.count()).select_from(StockMove)

        if current_user.role.strip().lower() != "admin":
            statement = statement.where(StockMove.user_id == current_user.id)

        statement = statement.group_by(StockMove.move_type)
        result = await db.execute(statement)
        results = result.all()

        count = {"incoming": 0, "outgoing": 0}
        for move_type, quantity in results:
            if move_type in count:
                count[move_type] = quantity

        return [
            {"move_type": "incoming", "quantity": count["incoming"]},
            {"move_type": "outgoing", "quantity": count["outgoing"]},
        ]

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
