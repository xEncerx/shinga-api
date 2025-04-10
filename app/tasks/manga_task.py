from sqlmodel import Session, select, and_
from datetime import datetime, timezone
from asyncio import sleep

from app.services.manga_api import manga_api
from app.core.database import engine
from app.core import settings, MC
from app.models import Mangas
from app.utils import logger


async def manga_updater_task() -> None:
    with Session(engine) as session:
        time_threshold = datetime.now(timezone.utc) - settings.MIN_UPDATE_INTERVAL

        mangas = session.exec(
            select(Mangas).where(
                and_(
                    Mangas.last_update < time_threshold,
                    Mangas.status != MC.Status.RELEASED,
                    Mangas.status != MC.Status.ANONS,
                ),
            )
        ).all()

        for manga in mangas:
            try:
                manga_data = (
                    await manga_api.search_by_source(
                        query=manga.slug,
                        source=manga.source_name,
                    ),
                ).content

                if not manga_data:
                    continue

                manga_data = manga_data[0]

                manga.alt_names = manga_data.alt_names
                manga.description = manga_data.description
                manga.avg_rating = manga_data.avg_rating
                manga.views = manga_data.views
                manga.chapters = manga_data.chapters
                manga.cover = manga_data.cover
                manga.status = manga_data.status
                manga.translate_status = manga_data.translate_status
                manga.year = manga_data.year
                manga.genres = manga_data.genres
                manga.categories = manga_data.categories
                manga.last_update = manga_data.last_update

                session.add(manga)
                session.commit()

                logger.info(f"Successfully updated manga {manga.id}")
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating manga {manga.id}: {e}")

            await sleep(5)
