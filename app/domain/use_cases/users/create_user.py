from typing import Any

from app.infrastructure.db.crud.user import UserCRUD
from app.infrastructure.db.models import User
from app.domain.models.exceptions import *
from app.core.security import *


async def create_user(
    username: str,
    email: str,
    password: str | None = None,
    yandex_id: str | None = None,
    google_id: str | None = None,
    extra_data: dict[str, Any] | None = None,
    is_stuff: bool = False,
    is_superuser: bool = False,
) -> User:
    """
    Create a new user with the provided details.

    Args:
        username (str): The username for the new user.
        email (str): The email address for the new user.
        password (str | None): The password for the new user. If None, a random password will be generated.
        yandex_id (str | None): The Yandex ID for the new user. Defaults to None.
        google_id (str | None): The Google ID for the new user. Defaults to None.
        avatar (str): The avatar URL for the new user. Defaults to the base user avatar.
        extra_data (dict[str, Any] | None): Additional data for the user. Defaults to None.
        is_stuff (bool): Whether the user is a staff member. Defaults to False.
        is_superuser (bool): Whether the user is a superuser. Defaults to False.
    """
    if await UserCRUD.read.user(username=username):
        raise UserAlreadyExistsError(f"Username '{username}' is already taken.")
    if await UserCRUD.read.user(email=email):
        raise UserAlreadyExistsError(f"Email '{email}' is already registered.")

    if google_id or yandex_id or not password:
        # If the user is registering with OAuth, we generate a random password
        password = generate_random_password()
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_staff=is_stuff,
        is_superuser=is_superuser,
        extra_data=extra_data,
        google_id=google_id,
        yandex_id=yandex_id,
    )
    await UserCRUD.create.user(user)
    
    return user
