from abc import ABC, abstractmethod

__all__ = ["IDataValidator"]


class IDataValidator(ABC):
    """Interface for data validation"""

    @abstractmethod
    def validate(self, data: str) -> tuple[bool, list[str]]:
        """Returns (is_valid, errors)"""
        pass
