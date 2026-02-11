from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

__all__ = ["ITokenService"]


class ITokenService(ABC):
    """Interface for token operations"""

    @abstractmethod
    def create_access_token(self, sub: str, expires_delta: timedelta) -> str:
        """Create a access token with an expiration time"""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify a JWT token and return the decoded payload"""
        pass
