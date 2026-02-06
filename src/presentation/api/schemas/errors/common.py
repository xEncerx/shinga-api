from .base import *

__all__ = [
    "InternalServerError",
]


class InternalServerError(BaseAPIException):
    """Exception raised for internal server errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    details = ["Internal server error occurred."]
