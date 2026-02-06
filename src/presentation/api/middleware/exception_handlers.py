from pydantic import ValidationError as PydanticValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status
from typing import Union

from src.presentation.api.schemas.errors import BaseAPIException

__all__ = [
    "base_api_exception_handler",
    "pydantic_validation_exception_handler",
]


def create_error_response(
    status_code: int,
    error_class_name: str,
    details: list[str],
    headers: dict | None = None,
) -> JSONResponse:
    """Creates a standardized JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "error": error_class_name,
            "details": details,
        },
        headers=headers,
    )


async def base_api_exception_handler(
    request: Request,
    exc: BaseAPIException,
) -> JSONResponse:
    """Handles BaseAPIException and formats it into a consistent error response."""
    details = exc.details if isinstance(exc.details, list) else [str(exc.details)]
    return create_error_response(
        status_code=exc.status_code,
        error_class_name=exc.__class__.__name__,
        details=details,
        headers=exc.headers,
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError],
) -> JSONResponse:
    """Handles Pydantic validation errors and formats them into a consistent error response."""
    details = []

    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error["loc"])
        msg = error["msg"]
        details.append(f"{loc}: {msg}")

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_class_name="ValidationError",
        details=details,
    )
