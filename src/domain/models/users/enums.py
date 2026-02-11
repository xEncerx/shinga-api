from enum import Enum

__all__ = ["UserRole"]


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    STAFF = "STAFF"
    MODERATOR = "MODERATOR"
