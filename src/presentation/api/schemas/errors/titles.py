from .base import BaseAPIException

__all__ = ["TitleNotFound"]


class TitleNotFound(BaseAPIException):
    """Exception raised when the title is not found."""

    status_code = 404
    details = ["Title with the given ID not found."]
