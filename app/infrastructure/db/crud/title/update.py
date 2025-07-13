from ...session import get_session
from ...models import Title

from app.core import logger


class UpdateOperations:
    @staticmethod
    async def fields(title_id: str, **fields) -> bool:
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
                logger.error(f"Failed to update title: {e}")
                return False
