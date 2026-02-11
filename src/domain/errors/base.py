__all__ = [
    "DomainError",
    "ConflictError",
]


class DomainError(Exception):
    """Base class for domain-specific errors."""

    details: list[str]

    def __init__(
        self,
        details: list[str] | str,
    ) -> None:
        self.details = details if isinstance(details, list) else [details]


class ConflictError(DomainError):
    """Base class for conflict errors."""
