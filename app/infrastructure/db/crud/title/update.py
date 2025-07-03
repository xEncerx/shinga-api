from sqlalchemy.exc import IntegrityError

from ...session import get_session
from ...models import Title

from app.core import logger

async def update_title_fields(title_id: int | None, **fields) -> bool:
    """Update fields of an existing title in the database."""
    if not title_id or not fields:
        logger.error("Title ID and fields to update must be provided.")
        return False

    async with get_session() as session:
        try:
            title = await session.get(Title, title_id)
            if not title:
                logger.error(f"Title with ID {title_id} not found.")
                return False
            
            for key, value in fields.items():
                setattr(title, key, value)
            
            await session.commit()
            return True
        except IntegrityError as e:
            logger.error(f"Integrity error while updating title: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to update title: {e}")
            return False