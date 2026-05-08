from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from typing import Annotated, Callable
from fastapi import Depends

from src.presentation.api.dependencies import TokenServiceDep, SessionDep
from src.infrastructure.db.repositories import UserRepository
from src.presentation.api.schemas.errors import *
from src.domain.models.users import UserData
from src.domain.models.users.enums import UserRole

__all__ = ["GetUserDep", "GetOptionalUserDep", "require_roles"]


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/v1/auth/login/access-token",
)
optional_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/v1/auth/login/access-token",
    auto_error=False,  # Don't raise error if token is missing
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]
OptionalTokenDep = Annotated[str | None, Depends(optional_oauth2)]


async def get_user(
    token: TokenDep,
    token_service: TokenServiceDep,
    session: SessionDep,
) -> UserData:
    try:
        payload = token_service.verify_token(token)
        user_id = payload.get("sub")
        if user_id is None or user_id.isnumeric() is False:
            raise InvalidTokenCredentials()
    except (InvalidTokenError, ValidationError):
        raise InvalidTokenCredentials()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))

    if not user:
        raise UserNotFound()

    return user


async def get_optional_user(
    token: OptionalTokenDep,
    token_service: TokenServiceDep,
    session: SessionDep,
) -> UserData | None:
    """Get user if token is provided and valid, otherwise return None."""
    if token is None:
        return None

    try:
        payload = token_service.verify_token(token)
        user_id = payload.get("sub")
        if user_id is None or user_id.isnumeric() is False:
            return None
    except (InvalidTokenError, ValidationError):
        return None

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))

    return user


# === Role checking dependency ===
def require_roles(allowed_roles: list[UserRole]) -> Callable:
    async def role_checker(
        user: Annotated[UserData, Depends(get_user)],
    ) -> UserData:
        if user.role not in allowed_roles:
            raise ForbiddenError()
        return user

    return role_checker


# === Dependency Annotations ===
GetUserDep = Annotated[UserData, Depends(get_user)]
GetOptionalUserDep = Annotated[UserData | None, Depends(get_optional_user)]
AdminOnlyDep = Annotated[UserData, Depends(require_roles([UserRole.ADMIN]))]
