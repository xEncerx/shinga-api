from .base import *


__all__ = [
    "MissingCredentials",
    "InvalidCredentials",
    "InvalidTokenCredentials",
    "VerificationCodeNotFound",
    "InvalidVerificationCode",
]


class MissingCredentials(BaseAPIException):
    """Exception raised when neither username nor email is provided."""

    status_code = status.HTTP_401_UNAUTHORIZED
    details = ["Either username or email must be provided."]
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidCredentials(BaseAPIException):
    """Exception raised when the provided credentials are invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    details = ["Invalid username/email or password."]
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenCredentials(BaseAPIException):
    """Exception raised when the provided token is invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    details = ["Invalid user credentials"]
    headers = {"WWW-Authenticate": "Bearer"}


class VerificationCodeNotFound(BaseAPIException):
    """Exception raised when a verification code is not found for the given email."""

    status_code = status.HTTP_404_NOT_FOUND
    details = ["Verification code not found or expired for the provided email."]


class InvalidVerificationCode(BaseAPIException):
    """Exception raised when the provided verification code is invalid."""

    status_code = status.HTTP_400_BAD_REQUEST
    details = ["Invalid verification code."]
