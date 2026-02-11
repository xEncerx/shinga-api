from dataclasses import dataclass

from src.domain.models.users import UserData
from src.domain.interfaces import (
    IPasswordHasher,
    IDataValidator,
    IUserRepository,
)
from src.domain.errors import *
from src.core import settings


@dataclass
class RegisterUserResult:
    user_id: int
    username: str
    email: str


# TODO: add default avatar path


class RegisterUserUseCase:
    """Register a new user in the system."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        username_validator: IDataValidator,
        password_validator: IDataValidator,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._username_validator = username_validator
        self._password_validator = password_validator

    async def execute(
        self,
        username: str,
        email: str,
        password: str,
        google_id: str | None = None,
        yandex_id: str | None = None,
    ) -> RegisterUserResult:
        """
        Register a new user to the system.

        Args:
            username (str): The username of the user to be added.
            email (str): The email of the user to be added.
            password (str): The plaintext password for the user.
            google_id (str | None): Optional Google ID for OAuth users.
            yandex_id (str | None): Optional Yandex ID for OAuth users.

        Returns:
            RegisterUserResult: The result containing the new user's ID, username, and email.
        Raises:
            ValidationError: If the username or password validation fails.
            UserAlreadyExistsError: If a user with the same email or username already exists.
        """

        # 1.1 Validate password
        is_valid_password, password_errors = self._password_validator.validate(password)
        if not is_valid_password:
            raise ValidationError(password_errors)

        if username:
            # 1.2 Validate username
            is_valid_username, username_errors = self._username_validator.validate(
                username
            )
            if not is_valid_username:
                raise ValidationError(username_errors)

        # 2. Check if user already exists
        existing_user_by_email = await self._user_repository.get_by_email(email)
        if existing_user_by_email:
            raise UserAlreadyExistsError("email")

        # 3. Check if username is taken
        existing_user_by_username = await self._user_repository.get_by_username(
            username
        )
        if existing_user_by_username:
            raise UserAlreadyExistsError("username")

        # 4. Hash the password
        hashed_password = self._password_hasher.hash_password(password)

        # 5. Add user to the database
        user_id = await self._user_repository.add_user(
            UserData(
                username=username,
                email=email,
                hashed_password=hashed_password,
                avatar_path=settings.DEFAULT_AVATAR_URL,
            ),
            google_id=google_id,
            yandex_id=yandex_id,
        )

        return RegisterUserResult(
            user_id=user_id,
            username=username,
            email=email,
        )
