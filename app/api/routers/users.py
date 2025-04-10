from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

from app import crud
from app.core import limiter
from app.api.deps import SessionDep, CurrentUserDep
from app.core.security import *
from app.models import (
    UpdatePassword,
    UserCreate,
    UserRecoveryCode,
    Token,
    UserBase,
)

router = APIRouter(prefix=f"/users", tags=["users"])


def check_password(password: str) -> None:
    if not is_password_strong(password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number",
        )


@router.post("/login/access-token")
async def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.authenticate(
        session=session,
        username=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.username,
            expires_delta=access_token_expires,
        ),
    )


@router.post("/signup", response_model=UserRecoveryCode)
@limiter.limit("5/minute")
async def create_user(
    *,
    session: SessionDep,
    user_in: UserCreate,
    request: Request,
) -> Any:
    """
    Create new user.
    """
    user = await crud.get_user(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    check_password(user_in.password)

    user = await crud.create_user(session=session, user_create=user_in)

    return UserRecoveryCode(
        username=user.username,
        recovery_code=user.recovery_code,
        message="User successfully created",
    )


@router.get("/me", response_model=UserBase)
async def get_me(user: CurrentUserDep):
    """
    Get current user data (username).
    """
    return UserBase(username=user.username)


@router.patch("/me/password/update", response_model=UserRecoveryCode)
async def update_password_me(
    *,
    session: SessionDep,
    body: UpdatePassword,
    user: CurrentUserDep,
) -> Any:
    """
    Update own password.
    """
    if body.recovery_code != user.recovery_code:
        raise HTTPException(
            status_code=400,
            detail="Invalid recovery code",
        )
    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password",
        )
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the current one",
        )
    check_password(body.new_password)

    username = user.username

    new_recovery_code = generate_recovery_code()
    user.hashed_password = get_password_hash(body.new_password)
    user.recovery_code = new_recovery_code

    session.add(user)
    await session.commit()

    return UserRecoveryCode(
        username=username,
        recovery_code=new_recovery_code,
        message="Password successfully updated",
    )
