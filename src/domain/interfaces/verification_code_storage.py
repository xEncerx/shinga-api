from abc import ABC, abstractmethod
from datetime import timedelta

__all__ = ["IVerificationCodeStorage"]


class IVerificationCodeStorage(ABC):
    """Interface for storing and retrieving verification codes"""

    @abstractmethod
    async def store_code(self, key: str, code: str, expiration: timedelta) -> bool:
        """
        Store a verification code with expiration

        Args:
            key: Unique identifier for the code (e.g., user email)
            code: The verification code to store
            expiration: Time delta for code expiration

        Returns:
            bool: True if stored successfully
        """
        pass

    @abstractmethod
    async def get_code(self, key: str) -> str | None:
        """
        Retrieve a verification code

        Args:
            key: Unique identifier for the code

        Returns:
            str | None: The code if found and not expired, None otherwise
        """
        pass

    @abstractmethod
    async def delete_code(self, key: str) -> bool:
        """
        Delete a verification code

        Args:
            key: Unique identifier for the code

        Returns:
            bool: True if deleted successfully
        """
        pass

    @abstractmethod
    async def verify_and_delete(self, key: str, code: str) -> bool:
        """
        Verify a code and delete it if correct

        Args:
            key: Unique identifier for the code
            code: The code to verify

        Returns:
            bool: True if code matches and was deleted, False otherwise
        """
        pass
