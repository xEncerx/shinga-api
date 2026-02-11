from enum import Enum

__all__ = ["Language"]


class Language(str, Enum):
    """Supported application languages"""

    RU = "ru"
    EN = "en"

    @classmethod
    def default(cls) -> "Language":
        """Get default language"""
        return cls.RU
