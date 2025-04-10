from sqlmodel import Session, create_engine, text, select
from uuid import UUID

from app.core import settings
from app.utils import logger
from app.models import *

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db() -> None:
    with Session(engine) as session:
        try:
            session.exec(text("SELECT 1")).one()
            logger.info("Successfully connected to the database!")

        except Exception as _:
            session.rollback()
            logger.error("Failed to connect to the database!")


def is_manga_exists(manga_id: str) -> bool:
    """
    Check if a manga exists in the database by its ID.

    Args:
            manga_id (str): The unique identifier for the manga to check.

    Returns:
            bool: True if the manga exists in the database, False otherwise or if an error occurs.

    Raises:
            No exceptions are raised as they are caught internally and logged.
    """
    with Session(engine) as session:
        try:
            response = session.get(Mangas, manga_id)
            return response is not None
        except Exception as e:
            logger.error(f"Error checking if manga exists: {e}")
            return False


def upsert_user_manga(user_id: UUID, data: UpdateUserManga) -> bool:
    """
    Updates an existing user-manga association record or creates a new one if it doesn't exist.

    Args:
            user_id (UUID): The unique identifier of the user.
            data (UpdateUserManga): The data object containing manga_id, current_url, section, and last_read information.
    Returns:
            bool: True if the operation was successful, False otherwise.
    Raises:
            Exception: Any exceptions that occur during database operations are caught, logged,
                              and the transaction is rolled back.
    """
    with Session(engine) as session:
        try:
            stmt = select(UsersManga).where(
                UsersManga.user_id == user_id,
                UsersManga.manga_id == data.manga_id,
            )
            user_manga = session.exec(stmt).first()

            if user_manga:
                user_manga.current_url = data.current_url
                user_manga.section = data.section
                user_manga.last_read = data.last_read
            else:
                new_user_manga = UsersManga(
                    user_id=user_id,
                    manga_id=data.manga_id,
                    current_url=data.current_url,
                    section=data.section,
                    last_read=data.last_read,
                )
                session.add(new_user_manga)

            session.commit()

            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user manga: {e}")
            return False


def add_manga(data: Mangas) -> bool:
    """
    Adds a manga record to the database.
    Args:
            data (Mangas): A Mangas model instance containing manga information to be added.
                                       The ID will be automatically generated from source_name and source_id.
    Returns:
            bool: True if manga was successfully added, False otherwise.
    Raises:
            Exception: Handled internally, logs error and returns False.
    """

    with Session(engine) as session:
        try:
            data.id = f"{data.source_name}|{data.source_id}"

            session.add(data)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error in add_manga: {str(e)}", exc_info=True)
            return False


def get_user_manga(
    user_id: UUID,
    section: MC.Section = MC.Section.ANY,
) -> list[UserMangaWithData | None]:
    """
    Retrieve manga entries associated with a specific user from the database.
    Args:
            user_id (UUID): The unique identifier of the user whose manga entries are being retrieved.
            section (MC.Section, optional): Filter results by section. Defaults to MC.Section.ANY,
                                                                            which returns manga from all sections.
    Returns:
            list[UserMangaWithData | None]: A list of UserMangaWithData objects containing combined information
                                                                            from both the UsersManga and Mangas tables. Returns an empty list
                                                                            if an error occurs during the database operation.
    """

    with Session(engine) as session:
        try:
            stmt = (
                select(UsersManga, Mangas)
                .join(Mangas, UsersManga.manga_id == Mangas.id)
                .where(UsersManga.user_id == user_id)
            )

            if section != MC.Section.ANY:
                stmt = stmt.where(UsersManga.section == section)

            results = session.exec(stmt).all()

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
            session.rollback()
            logger.error(f"Error in get_user_manga: {str(e)}", exc_info=True)
            return []
