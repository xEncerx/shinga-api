class DomainException(Exception):
    """Base class for domain exceptions."""

    message: str = "Domain error"

    def __init__(self, message: str | None = None):
        self.message = message or self.message

        super().__init__(self.message)


# --- User exceptions ---
class UserAlreadyExistsError(DomainException):
    message = "User already exists"


class UserNotFoundError(DomainException):
    message = "User not found"


class InvalidCredentialsError(DomainException):
    message = "Invalid credentials"


# --- Provider exceptions ---
class ProviderException(DomainException):
    """Base exception for provider errors."""

    message = "Provider error"


class RateLimitError(ProviderException):
    """Raised when API rate limit is exceeded (HTTP 429)."""

    message = "Rate limit exceeded"

    def __init__(self, message: str | None = None, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after  # Seconds to wait before retry


class ProviderUnavailableError(ProviderException):
    """Raised when provider is temporarily unavailable (HTTP 5xx)."""

    message = "Provider temporarily unavailable"


class ProviderDataError(ProviderException):
    """Raised when provider returns invalid/corrupted data."""

    message = "Invalid data from provider"
