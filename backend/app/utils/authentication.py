# This script handles authentication in our API using JWT (JSON Web Tokens)
# and password hashing with bcrypt.
# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

from datetime import (
    datetime,
    timedelta,
    timezone,
)  # To handle token expiration and timezones

from jwt import DecodeError
from app.utils.getenv import get_required_env
from fastapi import HTTPException, status
from passlib.context import (
    CryptContext,
)  # To hash and verify passwords securely with bcrypt
import jwt  # To create and decode JWT tokens
import os  # To access environment variables

# Secret key used to sign JWT tokens
SECRET_KEY = get_required_env("SECRET_KEY")

# JWT encryption algorithm
ALGORITHM = "HS256"

# Token expiration time (in minutes)
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION", 30))  # 30 minutes
REFRESH_TOKEN_DURATION = int(os.getenv("REFRESH_TOKEN_DURATION", 7))  # 7 days

# Password hashing context
# - CryptContext with bcrypt is used to securely hash passwords.
# - bcrypt is the recommended standard for storing passwords due to its salting and resistance to attacks.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Generates a secure hash for the given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the entered password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# Bcrypt uses "salting", so each hash generated is different.
# Even so, verify_password() can still confirm if they match.


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Creates a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# data → Contains user information (e.g., email or ID).
# The data is copied, expiration is added, and it's signed with SECRET_KEY and HS256.
# Returns a secure JWT token that the user will send in each request.


def decode_access_token(token: str):
    """Decodes a JWT token and returns the payload or raises an exception if invalid."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except (jwt.InvalidTokenError, DecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
