from .base import BaseValueManager
from app.core import settings


class ApiKeyManager(BaseValueManager):
    """
    API Key manager that handles OpenAI API key fetching, validation, and rate limiting.
    """

    def __init__(self):
        """
        Initialize the API key manager.

        Sets up rate limiting for API key usage:
        - 60 requests per minute per key
        """
        super().__init__()

        self.add_limit("rpm", max_requests=60, time_window=60, cooldown=60)

    async def fetch_values(self) -> list[str]:
        """
        Fetch OpenAI API keys from application settings.

        Returns:
            List of OpenAI API key strings
        """
        return settings.OPENAI_API_KEYS
    
    async def validate_value(self, value) -> bool:
        """
        Validate a single API key for basic format.

        Args:
            value: API key string to validate

        Returns:
            True if API key exists and is not empty, False otherwise
        """
        return True if value else False
