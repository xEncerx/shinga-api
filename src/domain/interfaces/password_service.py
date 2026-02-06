from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Interface for password hashing operations"""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Returns the hashed password"""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed password"""
        pass
