from sqlmodel import select, func

from ...models import User, UserTitles
from ...session import get_session

from app.core.security import verify_password
from app.core import logger


async def authenticate(username: str, password: str) -> User | None:
    async with get_session() as session:
        user = await session.get(User, {"username": username})

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        return user

async def is_username_available(username: str) -> bool:
    """Check if the username is available."""
    async with get_session() as session:
        try:
            data = await session.exec(
                select(User).where(func.lower(User.username) == username.lower())
            )
            return data.first() is None
        except Exception as e:
            logger.error(f"Failed to check username availability: {e}")
            return False


async def is_email_available(email: str) -> bool:
    """Check if the email is available."""
    async with get_session() as session:
        try:
            data = await session.exec(
                select(User).where(func.lower(User.email) == email.lower())
            )
            return data.first() is None
        except Exception as e:
            logger.error(f"Failed to check email availability: {e}")
            return False


async def oauth_user_exists(
    yandex_id: str | None = None,
    google_id: str | None = None,
) -> bool:
    if not (yandex_id or google_id):
        raise ValueError("At least one OAuth ID must be provided.")

    async with get_session() as session:
        try:
            if yandex_id:
                data = await session.exec(
                    select(User).where(User.yandex_id == yandex_id)
                )
            else:
                data = await session.exec(
                    select(User).where(User.google_id == google_id)
                )
            return data.first() is not None
        except Exception as e:
            logger.error(f"Failed to check OAuth user existence: {e}")
            return False
