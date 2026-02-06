from .base import *

__all__ = [
    "UserAlreadyExists",
    "UserNotFound",
    "UserTitleAlreadyExists",
    "UserTitleNotFound",
]


class UserAlreadyExists(BaseAPIException):
    """Exception raised when a user with the given username or email already exists."""

    status_code = status.HTTP_409_CONFLICT
    details = ["User with this username/email already exists."]


class UserNotFound(BaseAPIException):
    """Exception raised when the user is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    details = ["User not found."]


class UserTitleAlreadyExists(BaseAPIException):
    """Exception raised when a user title with the given title ID already exists for the user."""

    status_code = status.HTTP_409_CONFLICT
    details = ["User title with this title ID already exists for the user."]


class UserTitleNotFound(BaseAPIException):
    """Exception raised when a user title with the given title ID is not found for the user."""

    status_code = status.HTTP_404_NOT_FOUND
    details = ["User title with this title ID not found for the user."]
