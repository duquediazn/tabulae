from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Base schema for users.
    - Defines fields common to all user-related schemas.
    - `EmailStr` ensures the email is properly formatted.
    """

    name: str = Field(..., min_length=3, max_length=100, description="User's full name")
    email: EmailStr = Field(..., max_length=100, description="Valid email address")


class UserCreate(UserBase):
    """
    Schema for registering users.
    - `password`: Minimum of 8 characters required.
    - `role`: Defaults to 'user'; only accepts valid roles.
    - `is_active`: Defaults to False; must be activated by an admin.
    """

    password: str = Field(
        ..., min_length=8, max_length=255, description="Secure password (min. 8 chars)"
    )
    role: Optional[str] = Field(
        default="user",
        pattern="^(user|admin)$",
        description="User role (user/admin)",
    )
    is_active: Optional[bool] = Field(
        default=False, description="Active/inactive status"
    )


class UserUpdate(BaseModel):
    """
    Schema for updating users.
    - Allows updating `name`, `email`, `role`, `is_active`, and `password`.
    - Optional fields must not be empty.
    """

    name: Optional[str] = Field(
        None, min_length=3, max_length=100, description="New name"
    )
    email: Optional[EmailStr] = Field(
        None, max_length=100, description="New email address"
    )
    role: Optional[str] = Field(
        None, pattern="^(user|admin)$", description="New role (user/admin)"
    )
    is_active: Optional[bool] = None
    password: Optional[str] = Field(
        None, min_length=6, description="New password (optional)"
    )


class UserResponse(UserBase):
    """
    Schema for returning user information.
    - Includes `id`, `role`, and `is_active` for frontend/API usage.
    - Does not expose `password` for security reasons.
    """

    id: int
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }  # Enables conversion from ORM models to JSON


class PaginatedUserResponse(BaseModel):
    data: List[UserResponse]
    total: int
    limit: int
    offset: int

    model_config = {"from_attributes": True}


class BulkStatusUpdate(BaseModel):
    ids: List[int]
    is_active: bool
