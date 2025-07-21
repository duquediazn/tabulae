from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.database import get_db
from app.models.stock_move import StockMove
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.user import (
    BulkStatusUpdate,
    PaginatedUserResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.utils.authentication import hash_password
from app.dependencies import require_admin
from app.utils.validation import is_admin_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=PaginatedUserResponse)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: str = Query(None),
    is_active: bool = Query(None),
):
    """Lists all users (admin access only)."""
    try:
        statement = select(User)

        if is_active is not None:
            statement = statement.where(User.is_active == is_active)

        # Filter by name or email (case-insensitive)
        if search:
            search_like = f"%{search.lower()}%"
            statement = statement.where(
                func.lower(User.name).like(search_like)
                | func.lower(User.email).like(search_like)
            )

        total_records = db.exec(
            select(func.count()).select_from(statement.subquery())
        ).first()

        users = db.exec(statement.order_by(User.name).limit(limit).offset(offset)).all()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    return {"data": users, "total": total_records, "limit": limit, "offset": offset}


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Only an admin can create users and assign roles."""

    # Check if the email is already registered
    try:
        statement = select(User).where(User.email == user_data.email)
        existing_user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    # Validate role
    if user_data.role.lower() not in ["user", "admin"]:
        raise HTTPException(
            status_code=400, detail="Invalid role. Must be 'user' or 'admin'."
        )

    # Create user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role.lower(),
        is_active=user_data.is_active,
    )

    try:
        db.add(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while registering the user.",
        )
    db.commit()
    db.refresh(new_user)

    return new_user  # `UserResponse` automatically excludes the password


@router.get("/{id}", response_model=UserResponse)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve data for a specific user.
    - An **admin** can view any user.
    - A **regular user** can only view their own profile.
    """
    try:
        statement = select(User).where(User.id == id)
        user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not is_admin_user(current_user) and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user",
        )

    return user


@router.put("/bulk-status")
def bulk_update_user_status(
    data: BulkStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Allows an admin to activate or deactivate multiple users at once."""
    try:
        users = db.exec(select(User).where(User.id.in_(data.ids))).all()
        updated = []

        for user in users:
            if user.is_active == data.is_active:
                continue  # Already has the desired status

            # Optional rule:
            # Do not allow the current admin to deactivate themselves
            if data.is_active is False and user.id == admin.id:
                continue

            user.is_active = data.is_active
            db.add(user)
            updated.append(user)

        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error updating users",
        )

    return {
        "message": f"{len(updated)} users updated",
        "skipped": len(data.ids) - len(updated),
    }


@router.put("/{id}", response_model=UserResponse)
def update_user(
    id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allows a user to update their profile or an admin to edit any user."""

    # Search for the user in the database
    try:
        statement = select(User).where(User.id == id)
        user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if the current user is an admin
    is_admin = is_admin_user(current_user)

    # Permission control: only admin or the user themself can edit
    if not is_admin and user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this user",
        )

    # Apply changes (a regular user CANNOT change role or is_active)
    if user_update.name:
        user.name = user_update.name

    if user_update.email:
        # Check if the new email is already used by another user
        try:
            existing_user = db.exec(
                select(User).where(User.email == user_update.email, User.id != user.id)
            ).first()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal database error",
            )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use",
            )
        user.email = user_update.email

    if user_update.role:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to change the role",
            )
        if user_update.role.lower() not in ["user", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'user' or 'admin'.",
            )
        user.role = user_update.role.lower()

    if user_update.is_active is not None:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to change the is_active status",
            )
        user.is_active = user_update.is_active

    if user_update.password:
        user.password = hash_password(user_update.password)

    try:
        db.add(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Please verify the submitted data.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating the user.",
        )
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{id}", response_model=UserResponse)
def delete_user(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """Allows an admin to delete a user as long as they have no associated stock movements."""
    # Look for the user in the database
    try:
        user = db.exec(select(User).where(User.id == id)).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if the user has any stock movements
    try:
        statement = select(StockMove).where(StockMove.user_id == id)
        has_movements = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    if has_movements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete user because they have registered movements",
        )

    try:
        db.delete(user)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting the user",
        )
    db.commit()
    return user  # Returns the deleted user's data
