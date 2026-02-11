from datetime import timedelta
import redis.asyncio as redis

from src.domain.interfaces import IVerificationCodeStorage

__all__ = ["RedisVerificationCodeStorage"]


class RedisVerificationCodeStorage(IVerificationCodeStorage):
    """Redis implementation for storing verification codes"""

    def __init__(self, redis_client: redis.Redis, key_prefix: str = "verification:"):
        """
        Initialize Redis verification code storage

        Args:
            redis_client: Async Redis client instance
            key_prefix: Prefix for Redis keys
        """
        self._redis = redis_client
        self._key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        """Create full Redis key with prefix"""
        return f"{self._key_prefix}{key}"

    async def store_code(self, key: str, code: str, expiration: timedelta) -> bool:
        """
        Store a verification code in Redis with expiration

        Args:
            key: Unique identifier (e.g., user email)
            code: The verification code
            expiration: Time delta for expiration

        Returns:
            bool: True if stored successfully
        """
        try:
            redis_key = self._make_key(key)
            await self._redis.setex(
                redis_key,
                int(expiration.total_seconds()),
                code,
            )
            return True
        except Exception:
            return False

    async def get_code(self, key: str) -> str | None:
        """
        Retrieve a verification code from Redis

        Args:
            key: Unique identifier

        Returns:
            str | None: The code if found and not expired, None otherwise
        """
        try:
            redis_key = self._make_key(key)
            code = await self._redis.get(redis_key)
            if code:
                return code.decode("utf-8")
            return None
        except Exception:
            return None

    async def delete_code(self, key: str) -> bool:
        """
        Delete a verification code from Redis

        Args:
            key: Unique identifier

        Returns:
            bool: True if deleted successfully
        """
        try:
            redis_key = self._make_key(key)
            deleted = await self._redis.delete(redis_key)

            return bool(deleted)
        except Exception:
            return False

    async def verify_and_delete(self, key: str, code: str) -> bool:
        """
        Verify code matches and delete it atomically

        Args:
            key: Unique identifier
            code: The code to verify

        Returns:
            bool: True if code matches and was deleted
        """
        try:
            stored_code = await self.get_code(key)

            if stored_code is None:
                return False

            if stored_code != code:
                return False

            # Delete the code after successful verification
            await self.delete_code(key)
            return True

        except Exception:
            return False
