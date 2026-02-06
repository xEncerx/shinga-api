from sqlmodel.ext.asyncio.session import AsyncSession
from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Depends

from src.infrastructure.db.session import async_session

__all__ = ["SessionDep"]


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session


# === Dependencies Annotations ===
SessionDep = Annotated[AsyncSession, Depends(get_session)]
