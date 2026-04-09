import logging
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select
from app.models.product import Product
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse
from app.schemas.stock_move import StockMoveCreate

logger = logging.getLogger(__name__)


def _validate_movement_input(movement_data: StockMoveCreate) -> None:
    """Pure-Python validation of movement data before any DB interaction."""
    if not movement_data.lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The movement must contain at least one line.",
        )

    if len(movement_data.lines) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The maximum number of allowed lines is 100.",
        )

    if movement_data.move_type == "incoming":
        for line in movement_data.lines:
            if line.expiration_date and line.expiration_date <= date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"The line with product {line.product_id}, lot '{line.lot}', "
                        f"has an expired or same-day expiration date: {line.expiration_date}."
                    ),
                )


def _validate_active_warehouses(db: Session, warehouse_ids: list[int]) -> None:
    """Checks all warehouse IDs exist and are active. Raises 400 if any are not."""
    active_warehouses = db.exec(
        select(Warehouse.id).where(
            Warehouse.id.in_(warehouse_ids), Warehouse.is_active == True
        )
    ).all()

    missing = set(warehouse_ids) - set(active_warehouses)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following warehouses are inactive or do not exist: {missing}",
        )


def _validate_active_products(db: Session, product_ids: list[int]) -> None:
    """Checks all product IDs exist and are active. Raises 400 if any are not."""
    active_products = db.exec(
        select(Product.id).where(
            Product.id.in_(product_ids), Product.is_active == True
        )
    ).all()

    missing_products = set(product_ids) - set(active_products)
    if missing_products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following products are inactive or do not exist: {missing_products}",
        )


def create_stock_movement(
    movement_data: StockMoveCreate,
    user_id: int,
    db: Session,
) -> tuple[StockMove, list[StockMoveLine]]:
    """
    Creates a StockMove and its StockMoveLines in a single transaction.

    Validates input and entity constraints before persisting. Returns the
    committed and refreshed movement and lines, ready for serialization.

    Raises:
        HTTPException: on business rule violations or DB errors.
    """
    _validate_movement_input(movement_data)

    warehouse_ids = [line.warehouse_id for line in movement_data.lines]
    product_ids = [line.product_id for line in movement_data.lines]

    new_movement = StockMove(
        move_type=movement_data.move_type,
        user_id=user_id,
    )

    try:
        # Read-only validation queries first — no writes until both pass.
        _validate_active_warehouses(db, warehouse_ids)
        _validate_active_products(db, product_ids)

        db.add(new_movement)
        db.flush()  # Obtain new_movement.move_id for the FK in lines.

        created_lines: list[StockMoveLine] = []
        for i, line_data in enumerate(movement_data.lines, 1):
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
            created_lines.append(new_line)

        db.commit()
        db.refresh(new_movement)
        for line in created_lines:
            db.refresh(line)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Integrity error: duplicate or invalid reference.",
        )
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database internal server error",
        )

    return new_movement, created_lines
