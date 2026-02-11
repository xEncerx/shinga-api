from .base import DomainError


__all__ = [
    "PasswordResetError",
    "InvalidVerificationCodeError",
    "VerificationCodeNotFoundError",
    "EmailSendError",
    "TemplateRenderError",
]


class PasswordResetError(DomainError):
    """Base exception for password reset operations"""


class InvalidVerificationCodeError(PasswordResetError):
    """Raised when verification code is invalid or expired"""


class VerificationCodeNotFoundError(PasswordResetError):
    """Raised when verification code does not exist"""


class EmailSendError(PasswordResetError):
    """Raised when email sending fails"""


class TemplateRenderError(PasswordResetError):
    """Raised when template rendering fails"""
