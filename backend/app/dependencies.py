from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.routers.auth import get_current_user

def require_admin(user: User = Depends(get_current_user)) -> User:
    """Checks if the user is an administrator. Raises an exception if not."""
    if user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return user  # Returns the user if they are an admin
