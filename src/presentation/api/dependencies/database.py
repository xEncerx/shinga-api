from sqlmodel.ext.asyncio.session import AsyncSession
from collections.abc import AsyncGenerator
from functools import lru_cache
from redis.asyncio import Redis
from typing import Annotated
from fastapi import Depends

from src.infrastructure.db.session import async_session
from src.core import settings

__all__ = ["SessionDep", "RedisDep"]


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session


@lru_cache(1)
def get_redis_client() -> Redis:
    return Redis.from_url(str(settings.REDIS_DSN))


# === Dependencies Annotations ===
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]
