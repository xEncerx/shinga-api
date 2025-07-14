from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Request
from typing import Annotated

from ...schemas import Token, IncorrectUsernameOrPassword
from app.infrastructure.db.crud import UserCRUD
from app.core.security import *
from app.core import limiter

router = APIRouter()


@router.post("/login/access-token")
@limiter.limit("5/minute")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
) -> Token:
    """
    Generate access token for user authentication.

    **Limits: 5 requests per minute**

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username and password.

    Returns:
        Token: A token object containing the access token.

    Raises:
        UserNotFound: If the user is not found or the credentials are incorrect.
    """
    user = await UserCRUD.read.user(username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise IncorrectUsernameOrPassword()

    return Token(access_token=create_access_token(user.id))
