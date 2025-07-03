from .base import BaseValueManager
from app.core import settings

import aiofiles


class ApiKeyManager(BaseValueManager):
    """
    API Key manager that handles OpenAI API key fetching, validation, and rate limiting.
    """

    def __init__(self):
        """
        Initialize the API key manager.

        Sets up rate limiting for API key usage:
        - 10 requests per minute per key
        """
        super().__init__()

        self._api_keys_file = settings.CORE_PATH / "openai_api_keys.txt"  

        self.add_limit("rps", max_requests=1, time_window=8, cooldown=8)
        self.add_limit("rpm", max_requests=50, time_window=60, cooldown=60)
    
    async def validate_value(self, value) -> bool:
        """
        Validate a single API key for basic format.

        Args:
            value: API key string to validate

        Returns:
            True if API key exists and is not empty, False otherwise
        """
        return True if value else False
    
    async def fetch_values(self) -> list[str]:
        if not self._api_keys_file.exists():
            async with aiofiles.open(self._api_keys_file, "w"): ...
            return []
        
        async with aiofiles.open(self._api_keys_file, mode='r') as f:
            content = await f.read()

        keys = [line for i in content.splitlines() if (line := i.strip())]

        return list(set(keys))
