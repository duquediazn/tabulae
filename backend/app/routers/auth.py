from datetime import timedelta, datetime, timezone
import os
from fastapi import Request, Response
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.dependencies import get_current_user, oauth2
from app.utils.getenv import get_required_env
from app.schemas.auth import PasswordCheckRequest
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.database import get_db
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.schemas.user import UserSelfRegister, UserResponse
from app.utils.authentication import (
    ACCESS_TOKEN_DURATION,
    REFRESH_TOKEN_DURATION,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
)

is_production = get_required_env("ENVIRONMENT", fallback="development") == "production"

router = APIRouter(prefix="/auth", tags=["Authentication"])

### USER REGISTRATION ###
@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserSelfRegister, db: Session = Depends(get_db)):
    """Registers a new user with encrypted password."""
    # Create user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role="user",  # Always assign role "user"
        is_active=False,  # Inactive by default
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while registering user.",
        )

    return new_user  


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

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."   
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive. Please contact an administrator to activate your account.",
        )
    
    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_DURATION),
    )
    refresh_token = create_refresh_token(
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
        secure=is_production,
        samesite="lax" if not is_production else "none",
        path="/auth/", 
        max_age=REFRESH_TOKEN_DURATION * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

### GET AUTHENTICATED USER DATA ###
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

    payload = decode_access_token(refresh_token, expected_type="refresh")

    jti = payload.get("jti")
    try:
        if jti and db.get(RevokedToken, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked.",
            )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error.",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
        )
    user_id = int(user_id_str)

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
def logout(
    request: Request,
    response: Response,
    token: str = Depends(oauth2),
    db: Session = Depends(get_db),
):
    """Deletes the refresh token cookie and revokes the access and refresh tokens when the user logs out."""

    response.delete_cookie(
        key="refresh_token",
        path="/auth/", 
        secure=is_production,
        samesite="lax" if not is_production else "none",
    )

    # Revoke both the access token and the refresh token by storing their JTIs.
    try:
        access_payload = decode_access_token(token)
        access_jti = access_payload.get("jti")
        access_exp = access_payload.get("exp")
        if access_jti and access_exp:
            db.add(RevokedToken(
                jti=access_jti,
                expires_at=datetime.fromtimestamp(access_exp, timezone.utc),
            ))

        refresh_token_value = request.cookies.get("refresh_token")
        if refresh_token_value:
            try:
                refresh_payload = decode_access_token(refresh_token_value)
                refresh_jti = refresh_payload.get("jti")
                refresh_exp = refresh_payload.get("exp")
                if refresh_jti and refresh_exp:
                    db.add(RevokedToken(
                        jti=refresh_jti,
                        expires_at=datetime.fromtimestamp(refresh_exp, timezone.utc),
                    ))
            except HTTPException:
                pass  # If the refresh token is invalid or expired, we can ignore it since it's already unusable.

        db.commit()
    except HTTPException:
        pass  
    except IntegrityError:
        db.rollback()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error while revoking token.",
        )

    return {"message": "Logged out successfully"}
