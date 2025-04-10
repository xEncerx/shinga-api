from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Any
import random
import jwt
import re

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def is_password_strong(password: str) -> bool:
    pattern = r"^(?=.*[A-Z])(?=.*[a-z]).{8,}$"
    return bool(re.fullmatch(pattern, password))


def generate_recovery_code() -> str:
    return str(random.randint(100000000, 999999999))
