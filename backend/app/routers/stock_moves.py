from datetime import date, datetime, time, timezone
from dateutil.relativedelta import relativedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select
from sqlalchemy.exc import SQLAlchemyError
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
from app.routers.auth import get_current_user
from app.schemas.stock_move_line import (
    StockMoveLineResponse,
    PaginatedStockMoveLineWithNamesResponse,
)
from app.utils.validation import is_admin_user
from app.routers.websocket import manager
import anyio


router = APIRouter(prefix="/stock-movements", tags=["Stock Movements"])


@router.get("/", response_model=PaginatedStockMovesResponse)
def get_movements(
    db: Session = Depends(get_db),
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
            statement = statement.where(StockMove.created_at >= date_from)

        if date_to:
            statement = statement.where(StockMove.created_at <= date_to)

        if user_id and is_admin_user(current_user):
            statement = statement.where(StockMove.user_id == user_id)

        if not is_admin_user(current_user):
            statement = statement.where(StockMove.user_id == current_user.id)

        results = db.exec(
            statement.order_by(StockMove.created_at.desc()).limit(limit).offset(offset)
        ).all()

        total_records = (
            db.exec(select(func.count()).select_from(statement.subquery())).first() or 0
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    movements_response = []

    for movement, user_name in results:
        try:
            movement_lines = db.exec(
                select(StockMoveLine)
                .where(StockMoveLine.move_id == movement.move_id)
                .order_by(StockMoveLine.line_id)
            ).all()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error",
            )

        movements_response.append(
            StockMoveResponse(
                move_id=movement.move_id,
                created_at=movement.created_at,
                move_type=movement.move_type,
                user_id=movement.user_id,
                user_name=user_name,
                lines=[
                    StockMoveLineResponse.model_validate(line)
                    for line in movement_lines
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
def get_movements_last_year(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns movements from the last year. Filters by user if not admin."""
    date_to = datetime.combine(datetime.now(timezone.utc).date(), time.max).replace(
        tzinfo=timezone.utc
    )
    date_from = date_to - relativedelta(years=1)

    try:
        statement = (
            select(StockMove)
            .where(StockMove.created_at >= date_from)
            .where(StockMove.created_at <= date_to)
        )

        if not is_admin_user(current_user):
            statement = statement.where(StockMove.user_id == current_user.id)

        statement = statement.order_by(StockMove.created_at.desc())
        results = db.exec(statement).all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return [
        StockMoveLastYearGraph(
            move_id=row.move_id,
            user_id=row.user_id,
            created_at=row.created_at,
            move_type=row.move_type,
        )
        for row in results
    ]


@router.get("/{move_id}", response_model=StockMoveResponse)
def get_movement(
    move_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves the details of a specific movement along with its lines.
    - **Regular users** can only view their own movements.
    - **Admins** can view any movement.
    """
    try:
        statement = select(StockMove).where(StockMove.move_id == move_id)
        movement = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movement not found"
        )

    # If not admin and the movement does not belong to the authenticated user, deny access
    if not is_admin_user(current_user) and movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this movement.",
        )

    # Retrieve the user associated with the movement
    try:
        user = db.exec(select(User.name).where(User.id == movement.user_id)).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving the user associated with the movement.",
        )

    # Retrieve movement lines
    try:
        statement_lines = select(StockMoveLine).where(
            StockMoveLine.move_id == movement.move_id
        )
        movement_lines = db.exec(statement_lines).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving the movement lines.",
        )

    return StockMoveResponse(
        move_id=movement.move_id,
        created_at=movement.created_at,
        move_type=movement.move_type,
        user_id=movement.user_id,
        user_name=user or "Unknown",
        lines=[StockMoveLineResponse.model_validate(line) for line in movement_lines],
    )


@router.post("/", response_model=StockMoveResponse, status_code=status.HTTP_201_CREATED)
def create_movement(
    movement_data: StockMoveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Registers a stock movement with all its lines in a single request.

    - A **regular user** can only register movements for themselves.
    - An **admin** can register movements for any user.
    - If a product is inactive, the operation is interrupted.
    - If a warehouse is inactive, the operation is interrupted.
    """

    # Not admin users can only register their own stock movements
    if not is_admin_user(current_user) and movement_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot register a movement for another user.",
        )

    if not movement_data.lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The movement must contain at least one line.",
        )

    # Prevent registering products with expired expiration dates.
    for line in movement_data.lines:
        if (
            line.expiration_date
            and line.expiration_date <= date.today()
            and movement_data.move_type == "incoming"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"The line with product {line.product_id}, lot '{line.lot}', "
                    f"has an expired or same-day expiration date: {line.expiration_date}."
                ),
            )

    # Maximum number of lines per movement
    if len(movement_data.lines) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The maximum number of allowed lines is 100.",
        )

    # Create the stock movement
    new_movement = StockMove(
        move_type=movement_data.move_type,
        user_id=movement_data.user_id,
    )

    try:
        db.add(new_movement)
        db.flush()

        warehouses = [line.warehouse_id for line in movement_data.lines]
        products = [line.product_id for line in movement_data.lines]

        active_warehouses = db.exec(
            select(Warehouse.id).where(
                Warehouse.id.in_(warehouses), Warehouse.is_active == True
            )
        ).all()

        diff = set(warehouses) - set(active_warehouses)
        if diff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The following warehouses are inactive or do not exist: {diff}",
            )

        active_products = db.exec(
            select(Product.id).where(
                Product.id.in_(products), Product.is_active == True
            )
        ).all()

        diff = set(products) - set(active_products)
        if diff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The following products are inactive or do not exist: {diff}",
            )

        # Add the movement lines (if present)
        for i, line_data in enumerate(movement_data.lines, 1):

            # Creates stock movement lines
            new_line = StockMoveLine(
                move_id=new_movement.move_id,
                line_id=i,
                warehouse_id=line_data.warehouse_id,
                product_id=line_data.product_id,
                lot=line_data.lot or "NO_LOT",
                expiration_date=line_data.expiration_date,
                quantity=line_data.quantity,
            )
            db.add(new_line)

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        msg_error = (str(e.orig) if hasattr(e, "orig") else str(e)).split("\n")[0]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity error: {msg_error}",
        )
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database internal server error",
        )

    # Retrieve user associated with the movement
    try:
        user_name = db.exec(
            select(User.name).where(User.id == movement_data.user_id)
        ).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving the user associated with the movement",
        )

    # Retrieve associated lines
    try:
        movement_lines = db.exec(
            select(StockMoveLine).where(StockMoveLine.move_id == new_movement.move_id)
        ).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    # Send message to all connected WebSocket clients
    try:
        mensaje = f"New stock movement recorded: {new_movement.move_id} ({new_movement.move_type})"

        # Asynchronous function to broadcast the message
        async def emitir_websocket_mensaje(mensaje: str):
            await manager.broadcast(mensaje)

        """
        AnyIO is used to emit a WebSocket message asynchronously from a synchronous route, 
        ensuring compatibility with FastAPI's event loop.
        """

        anyio.from_thread.run(emitir_websocket_mensaje, mensaje)

    except Exception as e:
        print("Error while emitting WebSocket:", str(e))

    # Return the object with its lines
    return StockMoveResponse(
        move_id=new_movement.move_id,
        created_at=new_movement.created_at,
        move_type=new_movement.move_type,
        user_id=new_movement.user_id,
        user_name=user_name or "Unknown",
        lines=[StockMoveLineResponse.model_validate(line) for line in movement_lines],
    )


@router.get("/{move_id}/lines", response_model=PaginatedStockMoveLineWithNamesResponse)
def get_movement_lines(
    move_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Lists all lines of a movement with product and warehouse names."""

    try:
        statement = select(StockMove).where(StockMove.move_id == move_id)
        movement = db.exec(statement).first()
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

    if not is_admin_user(current_user) and movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this movement",
        )

    try:
        statement_lines = (
            select(StockMoveLine, Product.short_name, Warehouse.description)
            .join(Product, Product.id == StockMoveLine.product_id)
            .join(Warehouse, Warehouse.id == StockMoveLine.warehouse_id)
            .where(StockMoveLine.move_id == move_id)
            .order_by(StockMoveLine.line_id)
        )

        results = db.exec(statement_lines.limit(limit).offset(offset)).all()
        total_records = (
            db.exec(
                select(func.count()).select_from(statement_lines.subquery())
            ).first()
            or 0
        )

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
def count_movements_by_move_type(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Counts the number of stock movements grouped by move type (incoming, outgoing)."""
    try:
        statement = select(StockMove.move_type, func.count()).join(
            User, StockMove.user_id == User.id
        )

        if not is_admin_user(current_user):
            statement = statement.where(StockMove.user_id == current_user.id)

        statement = statement.group_by(StockMove.move_type)
        results = db.exec(statement).all()

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
