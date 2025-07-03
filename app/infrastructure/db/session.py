from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool

from fastapi import Depends

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from app.core import settings

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    connect_args={"server_settings": {"timezone": "UTC"}},
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=AsyncAdaptedQueuePool,
    future=True,
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
