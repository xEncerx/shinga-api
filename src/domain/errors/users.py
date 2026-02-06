from .base import ConflictError, DomainError


__all__ = [
    "UserAlreadyExistsError",
    "UserNotFoundError",
]


class UserAlreadyExistsError(ConflictError):
    """User already exists."""

    def __init__(self, field: str) -> None:
        super().__init__([f"A user with this {field} already exists"])


class UserNotFoundError(DomainError):
    """User not found."""

    def __init__(self, identifier: str | None = None) -> None:
        detail = "User %s not found"
        if identifier:
            detail = detail % f"with identifier '{identifier}'"
        super().__init__([detail])
