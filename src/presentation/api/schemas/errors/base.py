from fastapi import HTTPException, status
from typing import Any

__all__ = [
    "BaseAPIException",
    "status",
]


class BaseAPIException(HTTPException):
    """Base class for API exceptions with additional fields."""

    status_code: int
    details: list[str]
    headers: dict[str, Any] | None = None

    def __init__(
        self,
        details: list[str] | None = None,
        headers: dict[str, Any] | None = None,
        **extra: Any
    ):
        self.details = (
            details if details is not None else getattr(self.__class__, "details", [])
        )
        super().__init__(
            status_code=self.status_code,
            detail=self.details,
            headers=headers or self.headers,
        )
        self.extra = extra
