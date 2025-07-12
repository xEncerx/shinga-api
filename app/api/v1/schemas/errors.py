from fastapi import HTTPException, status
from typing import Any

# Base class for API exceptions
class BaseAPIException(HTTPException):
    """Base class for API exceptions with additional fields."""
    status_code: int
    detail: str
    headers: dict[str, Any] | None = None

    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, Any] | None = None,
        **extra: Any
    ):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=headers or self.headers,
        )
        self.extra = extra

# Base class for user-related exceptions
class UserRelatedError(BaseAPIException):
    """User related error exception."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "User related error"

# Base class for title-related exceptions
class TitleRelatedError(BaseAPIException):
    """Title related error exception."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Title related error"

# Base class for OAuth-related exceptions
class OAuthError(BaseAPIException):
    """OAuth error exception."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "OAuth error"

# Base class for email-related exceptions
class EmailError(BaseAPIException):
    """Email error exception."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email error"

# --- User exceptions ---
class UserAlreadyExists(UserRelatedError):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"

class UserNotFound(UserRelatedError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"

class UserNotAuthorized(UserRelatedError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "User not authorized"
    headers = {"WWW-Authenticate": "Bearer"}

class PasswordTooWeak(UserRelatedError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Password is too weak. It must contain at least one uppercase letter, one lowercase letter, and be at least 8 characters long."

class InvalidUserCredentials(UserRelatedError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid user credentials"
    headers = {"WWW-Authenticate": "Bearer"}

# --- Title exceptions ---
class TitleNotFound(TitleRelatedError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Title not found"

# --- Email exceptions ---
class EmailNotSent(EmailError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Email could not be sent"

class EmailAlreadySent(EmailError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email already sent"

class EmailCodeMismatch(EmailError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email code mismatch"

# --- Other exceptions ---
class ValidationError(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"