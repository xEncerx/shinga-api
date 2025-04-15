from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone
from sqlmodel import select, and_

from ..engine import engine

from app.core import MC, settings
from app.utils import logger
from app.models import *


async def is_manga_exists(manga_id: str) -> bool:
    """
    Check if manga with the given ID exists in the database.
    Args:
        manga_id (str): The unique identifier of the manga to check.

    Returns:
        bool: True if the manga exists, False otherwise or if an error occurs.

    Raises:
        No exceptions are raised as they are caught internally and logged.
    """
    async with AsyncSession(engine) as session:
        try:
            response = await session.get(Manga, manga_id)
            return response is not None
        except Exception as e:
            logger.error(f"Error checking if manga exists: {e}")
            return False


async def upsert_user_manga(username: str, data: UpdateUserManga) -> bool:
    """
    Upsert (update or insert) a user's manga reading state in the database.
    This function checks if a record for the specified user and manga exists:
    - If it exists, it updates the current URL, section, and last read timestamp.
    - If it doesn't exist, it creates a new record with the provided data.
    Args:
        username (str): The username of the user.
        data (UpdateUserManga): Object containing manga details including:
            - manga_id: Identifier of the manga
            - current_url: URL of the current page being read
            - section: Current section of the manga
            - last_read: Timestamp of when the manga was last read
    Returns:
        bool: True if the operation was successful, False if an error occurred.
    Raises:
        No exceptions are raised as they are caught internally and logged.
    """
    async with AsyncSession(engine) as session:
        try:
            stmt = select(UserManga).where(
                UserManga.username == username,
                UserManga.manga_id == data.manga_id,
            )
            user_manga = (await session.exec(stmt)).first()

            if user_manga:
                user_manga.current_url = data.current_url or user_manga.current_url
                user_manga.section = data.section or user_manga.section
                user_manga.last_read = data.last_read
            else:
                new_user_manga = UserManga(
                    username=username,
                    manga_id=data.manga_id,
                    current_url=data.current_url,
                    section=data.section,
                    last_read=data.last_read,
                )
                session.add(new_user_manga)

            await session.commit()

            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating user manga: {e}")
            return False


async def add_manga(data: Manga) -> bool:
    """
    Adds a manga record to the database.
    Parameters:
        data (Manga): The manga object containing all manga information to be stored.
    Returns:
        bool: True if the manga was successfully added, False otherwise.
    Raises:
        No exceptions are raised as they are caught internally and logged.
        In case of exceptions, the transaction is rolled back.
    Example:
        ```
        manga_data = Manga(
            source_name="remanga",
            source_id="12345",
            title="Example Manga",
            ...
        )
        success = await add_manga(manga_data)
        ```
    """
    async with AsyncSession(engine) as session:
        try:
            data.id = f"{data.source_name}|{data.source_id}"

            session.add(data)
            await session.commit()
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in add_manga: {str(e)}", exc_info=True)
            return False


async def get_updatable_manga() -> list[Manga]:
    time_threshold = datetime.now(timezone.utc) - settings.MIN_UPDATE_INTERVAL

    async with AsyncSession(engine) as session:
        try:
            stmt = select(Manga).where(
                and_(
                    Manga.last_update < time_threshold,
                    Manga.status != MC.Status.RELEASED,
                    Manga.status != MC.Status.ANONS,
                ),
            )
            results = (await session.exec(stmt)).all()
            return results

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in get_updatable_manga: {str(e)}", exc_info=True)
            return []


async def get_user_manga(
    username: str,
    section: MC.Section = MC.Section.ANY,
) -> list[UserMangaWithData | None]:
    """
    Retrieve manga entries associated with a specific user, optionally filtered by section.
    Args:
        username (str): The username to search for.
        section (MC.Section, optional): Filter results by specific section.
            Defaults to MC.Section.ANY, which returns manga from all sections.
    Returns:
        list[UserMangaWithData | None]: A list of UserMangaWithData objects containing
            combined user manga tracking information and manga metadata. Returns an empty
            list if an error occurs during database operations.
    Raises:
        No exceptions are raised as they are caught and logged internally.
    """
    async with AsyncSession(engine) as session:
        try:
            stmt = (
                select(UserManga, Manga)
                .join(Manga, UserManga.manga_id == Manga.id)
                .where(UserManga.username == username)
            )

            if section != MC.Section.ANY:
                stmt = stmt.where(UserManga.section == section)

            results = (await session.exec(stmt)).all()

            return [
                UserMangaWithData(
                    current_url=um.current_url,
                    section=um.section,
                    last_read=um.last_read,
                    **manga.model_dump(),
                )
                for um, manga in results
            ]

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in get_user_manga: {str(e)}", exc_info=True)
            return []


async def get_user_manga_by_id(
    username: str,
    manga_id: str,
) -> UserMangaWithData | None:
    async with AsyncSession(engine) as session:
        try:
            stmt = (
                select(UserManga, Manga)
                .join(Manga, UserManga.manga_id == Manga.id)
                .where(UserManga.username == username)
                .where(Manga.id == manga_id)
            )
            result = (await session.exec(stmt)).first()

            return (
                UserMangaWithData(
                    current_url=result.UserManga.current_url,
                    section=result.UserManga.section,
                    last_read=result.UserManga.last_read,
                    **result.Manga.model_dump(),
                )
                if result
                else None
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Error in get_user_manga: {str(e)}", exc_info=True)
