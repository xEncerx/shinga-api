from .base import DomainError


__all__ = [
    "InvalidCredentialsError",
]


class AuthenticationError(DomainError):
    """Base class for authentication errors."""


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials."""
