from fastapi.exceptions import RequestValidationError
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded

import re


def exception_handler(_: Request, exc: HTTPException):
    """
    Built-in exception handler for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": exc.__class__.__name__,
            "detail": exc.detail,
        },
        headers=exc.headers,
    )


def pydantic_exception_handler(_: Request, exc: RequestValidationError):
    """
    Built-in exception handler for Pydantic validation errors.
    """
    first_error = exc.errors()[0] if exc.errors() else None

    return JSONResponse(
        status_code=422,
        content={
            "status_code": 422,
            "error": "ValidationError",
            "detail": (
                f"[{first_error['loc']}] {first_error['msg']}"
                if first_error
                else "Unknown"
            ),
        },
    )


def slowapi_exception_handler(_: Request, exc: RateLimitExceeded):
    """
    Built-in exception handler for SlowAPI rate limit errors.
    """
    return JSONResponse(
        status_code=429,
        content={
            "status_code": 429,
            "error": "RateLimitExceeded",
            "detail": f"Please be slow down. Try again later.",
        },
    )


def is_valid_email(email: str) -> bool:
    """
    Validate the format of an email address.
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None


def is_valid_username(username: str) -> bool:
    """
    Validate the format of a username. Only allows English letters, numbers, and (-_).
    """
    username_regex = r"^[a-zA-Z0-9_-]{3,20}$"
    return re.match(username_regex, username) is not None
