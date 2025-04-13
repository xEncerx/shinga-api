from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import text

from .engine import engine

from app.utils import logger


async def init_db() -> None:
    async with AsyncSession(engine) as session:
        try:
            (await session.exec(text("SELECT 1"))).one()
            logger.info("Successfully connected to the database!")

        except Exception as _:
            await session.rollback()
            logger.error("Failed to connect to the database!")
