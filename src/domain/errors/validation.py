from .base import DomainError


__all__ = [
    "ValidationError",
    "MissingCredentialsError",
]


class ValidationError(DomainError):
    """Base class for validation errors."""


class MissingCredentialsError(ValidationError):
    """Error indicating missing required credentials for authentication."""
