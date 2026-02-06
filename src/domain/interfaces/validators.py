from abc import ABC, abstractmethod


class IDataValidator(ABC):
    """Interface for data validation"""

    @abstractmethod
    def validate(self, data: str) -> tuple[bool, list[str]]:
        """Returns (is_valid, errors)"""
        pass
