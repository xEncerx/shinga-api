from .base import *

__all__ = [
    "ValidationError",
]


class ValidationError(BaseAPIException):
    """Base class for validation errors."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
