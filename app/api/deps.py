from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from collections.abc import AsyncGenerator
from pydantic import ValidationError
from typing import Annotated
import jwt

from app.models import User, TokenPayload
from app.core import settings, security
from app.db import engine

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"users/login/access-token",
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
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
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
