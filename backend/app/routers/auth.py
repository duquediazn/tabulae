"""
This file handles user authentication in the API, including:
- User registration (/auth/register) → Saves new users in the DB with hashed passwords.
- Login (/auth/login) → Verifies credentials and returns a JWT token.
- Get authenticated user data (/auth/profile) → Uses the JWT token to return user info.
"""

from datetime import timedelta
from fastapi import Request, Response
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.utils.authentication import (
    ACCESS_TOKEN_DURATION,
    REFRESH_TOKEN_DURATION,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

"""
- APIRouter → Creates a route group (/auth).
- Depends → Manages dependencies, like database and authentication.
- HTTPException → Raises HTTP errors with custom messages.
- status → Contains HTTP status codes (400, 401, etc.).
- OAuth2PasswordBearer → Handles OAuth2 auth with JWT tokens.
- get_db() → Retrieves a database session.
- UserCreate, UserResponse → Pydantic validation schemas.
- hash_password, verify_password, create_access_token, decode_access_token → Auth helper functions.
"""

# Router configuration
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 auth scheme configuration
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


### USER REGISTRATION ###
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user with encrypted password."""
    try:
        statement = select(User).where(User.email == user_data.email)
        existing_user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error.",
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    # Create user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role="user",  # Always assign role "user"
        is_active=False,  # Inactive by default
    )

    try:
        db.add(new_user)  # Adds object to the session context (pending commit)
    except IntegrityError:
        db.rollback()  # Rollback uncommitted changes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while registering user.",
        )

    db.commit()  # Commit current transaction
    db.refresh(new_user)  # Refresh instance with current DB values
    return new_user  # UserResponse will automatically exclude the password


### USER LOGIN ###
@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticates the user and generates a JWT token."""
    try:
        statement = select(User).where(
            User.email == form_data.username
        )  # OAuth2PasswordRequestForm expects 'username' and 'password' — we treat 'username' as email
        user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive. Please contact an administrator to activate your account.",
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials."
        )

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
    )
    refresh_token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(days=REFRESH_TOKEN_DURATION)
    )

    # Cookie settings explanation:
    #
    # In development:
    # - We are not using HTTPS, so 'secure' must be False.
    # - 'samesite' should be set to "lax" to allow cookies to be sent between different ports on localhost (e.g., 8080 and 8000).
    #
    # In production:
    # - 'secure' must be True to enforce HTTPS and allow cookies to be sent over secure connections.
    # - 'samesite' depends on your deployment:
    #     - If frontend and backend share the same domain (e.g., https://myapp.com), use 'lax'.
    #     - If frontend and backend are on different domains or subdomains (e.g., https://app.com and https://api.app.com),
    # use 'none' and make sure 'secure' is True, otherwise the cookie will be rejected by the browser.

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/auth/refresh",
        max_age=REFRESH_TOKEN_DURATION * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


### GET AUTHENTICATED USER DATA ###
def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    """Retrieves the current user based on the JWT token."""
    payload = decode_access_token(token)

    # Validate that the token contains the "sub" field
    user_id = int(payload["sub"])
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    # Check if the user still exists in the database
    try:
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or deleted.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive. Please contact an administrator to activate your account.",
        )

    return user


@router.get("/profile", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)):
    """Returns the authenticated user's data."""
    return user


### REFRESH TOKEN FOR AUTHENTICATED USER ###
@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Generates a new access token using the refresh token stored in an HttpOnly cookie."""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies.",
        )

    # decode_access_token() already handles InvalidTokenError and returns HTTP 401
    payload = decode_access_token(refresh_token)

    user_id = payload["sub"]

    try:
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deleted.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive. Please contact an administrator to activate your account.",
        )

    new_access_token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


### PASSWORD VERIFICATION ###
class PasswordCheckRequest(BaseModel):
    password: str


@router.post("/verify-password")
def verify_user_password(
    data: PasswordCheckRequest, current_user: User = Depends(get_current_user)
):
    """Verifies that the provided password matches the one stored for the authenticated user."""
    if not verify_password(data.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )
    return {"message": "Password verified successfully"}


### LOGOUT ###
@router.post("/logout")
def logout(response: Response):
    """Deletes the refresh token cookie when the user logs out."""
    response.delete_cookie(
        key="refresh_token", path="/auth/refresh", secure=True, samesite="none"
    )
    return {"message": "Logged out successfully"}
