from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from app.models.database import get_db
from app.utils.authentication import decode_access_token
from app.models.revoked_token import RevokedToken

# OAuth2 auth scheme configuration
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    """Retrieves the current user based on the JWT token."""
    payload = decode_access_token(token, expected_type="access")

    # Validate that the token contains the "sub" field
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )
    
    # Check if the token has been revoked by looking up its jti in the RevokedToken table.
    jti = payload.get("jti")
    if jti and db.get(RevokedToken, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked.")
    
    user_id = int(user_id_str)  # Convert user ID from string to integer

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


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Checks if the user is an administrator. Raises an exception if not."""
    if user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return user  # Returns the user if they are an admin
