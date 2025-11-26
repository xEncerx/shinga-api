from ...models import Title, TitleCover
from ...session import get_session

from app.core import logger


class UpdateOperations:
    @staticmethod
    async def fields(title_id: int, **fields) -> bool:
        """Update fields of an existing title in the database."""
        if not fields:
            raise ValueError("No fields provided for update")

        async with get_session() as session:
            try:
                title = await session.get(Title, title_id)
                if not title:
                    return False

                for key, value in fields.items():
                    setattr(title, key, value)

                await session.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to update title {title_id}: {e}", exc_info=True)
                return False

    @staticmethod
    async def title_cover(title_id: int, cover: TitleCover) -> bool:
        """Update the cover of an existing title in the database."""
        async with get_session() as session:
            try:
                title = await session.get(Title, title_id)
                if not title:
                    logger.warning(
                        f"Title with id={title_id} not found for cover update"
                    )
                    return False

                title.cover = cover

                await session.commit()
                return True
            except Exception as e:
                logger.error(
                    f"Failed to update cover for title_id {title_id}: {e}",
                    exc_info=True,
                )
                return False
