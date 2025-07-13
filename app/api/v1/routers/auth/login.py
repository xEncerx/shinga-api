from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from typing import Annotated

from ...schemas import Token, IncorrectUsernameOrPassword
from app.infrastructure.db.crud import UserCRUD
from app.core.security import *

router = APIRouter()


@router.post("/login/access-token")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Generate access token for user authentication.

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
