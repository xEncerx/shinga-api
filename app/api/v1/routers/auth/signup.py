from fastapi import APIRouter

from app.domain.models.exceptions import UserAlreadyExistsError
from app.core.security import is_password_strong, get_password_hash
from app.domain.use_cases import create_user
from ...schemas import *

router = APIRouter()

@router.post("/signup")
async def signup(user_in: UserIn) -> Message:
    """
    Sign up a new user.

    Args:
        user_in (UserIn): User input data containing username, email, and password.

    Returns:
        Message: A message indicating the success of the user creation.

    Raises:
        PasswordTooWeak: If the provided password does not meet strength requirements.
        UserAlreadyExists: If a user with the provided username or email already exists.
        UserRelatedError: If there is an error related to user creation, such as database issues.
    """
    if not is_password_strong(user_in.password):
        raise PasswordTooWeak()

    try:
        await create_user(
            username=user_in.username,
            email=user_in.email,
            password=get_password_hash(user_in.password)
        )

        return Message(message="User created successfully")
    except UserAlreadyExistsError as e:
        raise UserAlreadyExists(detail=e.message)
    except Exception as e:
        raise UserRelatedError(
            detail=str(e),
            status_code=500,
        )