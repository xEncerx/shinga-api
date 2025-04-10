from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from collections.abc import Generator
from pydantic import ValidationError
from typing import Annotated
from sqlmodel import Session
import jwt

from app.core import settings, engine, security
from app.models import Users, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"users/login/access-token",
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> Users:
    """
    Validates the access token and retrieves the current user from the database.
    Args:
            session: Database session dependency
            token: JWT token dependency
    Returns:
            Users: The current authenticated user
    Raises:
            HTTPException:
                    - 403 Forbidden: When the token is invalid or expired
                    - 404 Not Found: When the user associated with the token does not exist
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = session.get(Users, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


CurrentUserDep = Annotated[Users, Depends(get_current_user)]
