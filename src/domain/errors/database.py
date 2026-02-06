from .base import *

__all__ = ["DatabaseError", "RecordNotFoundError", "RecordAlreadyExistsError"]


class DatabaseError(DomainError):
    """Base class for database-related errors."""


class RecordNotFoundError(DatabaseError):
    """Error raised when a database record is not found."""


class RecordAlreadyExistsError(DatabaseError):
    """Error raised when a database record already exists."""
