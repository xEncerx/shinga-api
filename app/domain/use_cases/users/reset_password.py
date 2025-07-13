from pydantic import EmailStr

from app.infrastructure.db.crud.user import *
from app.domain.models.exceptions import *
from app.core.security import *


async def reset_user_password(email: EmailStr, new_password: str) -> None:
    """
    Resets the user's password.

    Args:
        email (EmailStr): The user's email address.
        new_password (str): The new password to set.

    Raises:
        UserNotFoundError: If the user with the given email does not exist.
    """
    hashed_password = get_password_hash(new_password)
    user = await UserCRUD.read.user(email=email)
    if not user:
        raise UserNotFoundError()

    await UserCRUD.update.fields(user.id, hashed_password=hashed_password)  # type: ignore
