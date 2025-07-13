from ...session import get_session
from ...models import User

from app.core import logger


class UpdateOperations:
    @staticmethod
    async def fields(user_id: int, **fields) -> bool:
        """Update user fields in the database."""
        if not fields:
            raise ValueError("No fields provided for update")

        async with get_session() as session:
            try:
                user = await session.get(User, user_id)
                if not user:
                    return False

                for key, value in fields.items():
                    setattr(user, key, value)

                await session.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to update user: {e}")
                return False
