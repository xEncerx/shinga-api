from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from typing import Annotated
from fastapi import Depends
import jwt

from .v1.schemas import TokenPayload, InvalidUserCredentials, UserNotFound
from app.infrastructure.db.crud.user import get_user
from app.infrastructure.db.models import User
from app.core import settings, security

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/v1/auth/login/access-token",
)


TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(token: TokenDep) -> User:
    """
    Retrieve the current authenticated user from the token.
    Args:
        session (SessionDep): The database session dependency.
        token (TokenDep): The JWT token dependency typically extracted from Authorization header.
    Returns:
        User: The authenticated user object.
    Raises:
        HTTPException:
            - 403 status code if the token is invalid or couldn't be decoded.
            - 404 status code if the user associated with the token doesn't exist.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise InvalidUserCredentials()

    user = await get_user(user_id=token_data.sub)
    if not user:
        raise UserNotFound()

    return user

async def get_superuser(token: TokenDep) -> User:
    user = await get_current_user(token)
    if not user.is_superuser:
        raise UserNotFound(detail="Superuser privileges required.")
    
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
SuperUserDep = Annotated[User, Depends(get_superuser)]
