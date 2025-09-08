from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Request
from typing import Annotated

from ...utils import is_valid_email, is_valid_username
from app.infrastructure.db.crud import UserCRUD
from app.core.security import *
from app.core import limiter
from ...schemas import *

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
        form_data (OAuth2PasswordRequestForm): Form data containing username or email and password.

    Returns:
        Token: A token object containing the access token.

    Raises:
        IncorrectUsernameOrPassword: If the user is not found or the credentials are incorrect.
    """
    username_or_email = form_data.username.strip()

    if "@" in username_or_email:
        if not is_valid_email(username_or_email):
            raise EmailValidationError()
        search_value = {"email": username_or_email}
    else:
        if not is_valid_username(username_or_email):
            raise UsernameValidationError()
        search_value = {"username": username_or_email}

    user = await UserCRUD.read.user(**search_value)  # type: ignore

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise IncorrectUsernameOrPassword()

    return Token(access_token=create_access_token(user.id))
