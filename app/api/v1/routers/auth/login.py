from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from typing import Annotated

from app.infrastructure.db.crud.user import authenticate
from ...schemas import Token, UserNotFound

router = APIRouter(tags=["auth"])


@router.post("/login/access-token")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Generate access token for user authentication.
    This endpoint allows users to log in using their username and password.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username and password.

    Returns:
        Token: A token object containing the access token.

    Raises:
        UserNotFound: If the user is not found or the credentials are incorrect.
    """
    user = await authenticate(
        username=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise UserNotFound(
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=form_data.username)
