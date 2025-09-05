from fastapi import APIRouter, Request
import re

from app.domain.models.exceptions import UserAlreadyExistsError
from app.core.security import is_password_strong
from app.domain.use_cases import create_user
from app.core import logger, limiter
from ...schemas import *

router = APIRouter()

def is_valid_username(username: str) -> bool:
    """Validate the username to ensure it contains only allowed characters."""
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))


@router.post("/signup")
@limiter.limit("5/minute")
async def signup(
    user_in: UserSignUp,
    request: Request,
) -> Message:
    """
    Sign up a new user.

    **Limits: 5 requests per minute**

    Args:
        user_in (UserSignUp): User input data containing username, email, and password.

    Returns:
        Message: A message indicating the success of the user creation.

    Raises:
        PasswordTooWeak: If the provided password does not meet strength requirements.
        UserAlreadyExists: If a user with the provided username or email already exists.
        UsernameValidationError: If the username contains invalid characters.
        UserRelatedError: If there is an error related to user creation, such as database issues.
    """
    if not is_password_strong(user_in.password):
        raise PasswordTooWeak()
    if not is_valid_username(user_in.username):
        raise UsernameValidationError()

    try:
        await create_user(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
        )

        return Message(message="User created successfully")
    except UserAlreadyExistsError as e:
        raise UserAlreadyExists(detail=e.message)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise UserRelatedError(status_code=500)
