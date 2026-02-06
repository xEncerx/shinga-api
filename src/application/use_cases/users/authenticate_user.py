from dataclasses import dataclass
from datetime import timedelta

from src.domain.interfaces import IUserRepository, ITokenService, IPasswordHasher
from src.domain.errors import InvalidCredentialsError, MissingCredentialsError
from src.domain.models.users import UserData


@dataclass
class AuthenticateUserResult:
    access_token: str
    token_type: str = "bearer"


class AuthenticateUserUseCase:
    """Authenticate user and issue access tokens"""

    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService,
        password_hasher: IPasswordHasher,
        expire_delta: timedelta,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service
        self._password_hasher = password_hasher
        self._expire_delta = expire_delta

    async def execute(
        self,
        username: str | None,
        email: str | None,
        plain_password: str,
    ) -> AuthenticateUserResult:
        """
        Authenticate a user by username or email and password.

        Args:
            username (str | None): The username of the user.
            email (str | None): The email of the user.
            plain_password (str): The plain text password provided by the user.

        Returns:
            AuthenticateUserResult: The result containing the access token.

        Raises:
            MissingCredentialsError: If neither username nor email is provided.
            InvalidCredentialsError: If the credentials are invalid.
        """
        if username is None and email is None:
            raise MissingCredentialsError(["Either username or email must be provided"])

        # 1. Retrieve user by username or email
        user: UserData | None = None
        if username is not None:
            user = await self._user_repository.get_by_username(username)
        elif email is not None:
            user = await self._user_repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError(["Invalid username/email or password"])

        # 2. Verify password
        is_password_correct = self._password_hasher.verify_password(
            plain_password,
            user.hashed_password,
        )
        if not is_password_correct:
            raise InvalidCredentialsError(["Invalid username/email or password"])

        # 3. Generate access token
        access_token = self._token_service.create_access_token(
            str(user.id),
            self._expire_delta,
        )

        return AuthenticateUserResult(access_token=access_token)
