from asyncio import sleep

from app.db.crud.manga import get_updatable_manga, add_manga
from app.services import manga_api
from app.utils import logger


async def manga_updater_task() -> None:
    mangas = await get_updatable_manga()
    if not mangas:
        logger.info("No mangas to update")
        return

    logger.info(f"Updating {len(mangas)} mangas")

    for manga in mangas:
        try:
            new_data = (
                await manga_api.search_by_source(
                    query=manga.slug,
                    source=manga.source_name,
                )
            ).content

            if not new_data:
                continue

            new_data = new_data[0]
            manga_id = manga.id

            manga.alt_names = new_data.alt_names
            manga.description = new_data.description
            manga.avg_rating = new_data.avg_rating
            manga.views = new_data.views
            manga.chapters = new_data.chapters
            manga.cover = new_data.cover
            manga.status = new_data.status
            manga.translate_status = new_data.translate_status
            manga.year = new_data.year
            manga.genres = new_data.genres
            manga.categories = new_data.categories
            manga.last_update = new_data.last_update

            await add_manga(manga)

            logger.info(f"Successfully updated manga {manga_id}")
        except Exception as e:
            logger.error(f"Error updating manga {manga_id}: {e}")

        await sleep(5)
