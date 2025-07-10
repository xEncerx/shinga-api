from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Any
import secrets
import random
import jwt
import re

from app.core import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = settings.ALGORITHM
DEFAULT_JWT_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES * timedelta(minutes=1)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta = DEFAULT_JWT_EXPIRE_MINUTES,
) -> str:
    """Create a JWT access token with an expiration time."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def is_password_strong(password: str) -> bool:
    """Check if the password is strong enough."""
    pattern = r"^(?=.*[A-Z])(?=.*[a-z]).{8,}$"
    return bool(re.fullmatch(pattern, password))


def generate_random_password(length: int = 12) -> str:
    """Generate a random password of specified length"""
    alphabet = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    )
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_code(size: int = 6) -> str:
    """Generate a random numeric code of specified size."""
    return str(random.randint(10 ** (size - 1), 10**size - 1))
