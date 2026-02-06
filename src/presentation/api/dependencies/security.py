from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from typing import Annotated
from fastapi import Depends

from src.presentation.api.dependencies import TokenServiceDep, SessionDep
from src.infrastructure.db.repositories import UserRepository
from src.presentation.api.schemas.errors import *
from src.domain.models.users import UserData

__all__ = ["GetUserDep"]

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/v1/auth/login/access-token",
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


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


# === Dependency Annotations ===
GetUserDep = Annotated[UserData, Depends(get_user)]
