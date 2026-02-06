from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    STAFF = "STAFF"
    MODERATOR = "MODERATOR"
