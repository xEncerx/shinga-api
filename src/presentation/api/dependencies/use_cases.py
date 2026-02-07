from datetime import timedelta
from typing import Annotated
from fastapi import Depends


from src.presentation.api.dependencies.security import TokenServiceDep
from src.presentation.api.dependencies.database import SessionDep
from src.presentation.api.dependencies.services import (
    PasswordHasherDep,
    PasswordValidatorDep,
    UsernameValidatorDep,
)
from src.infrastructure.db.repositories import (
    UserRepository,
    UserTitleRepository,
    TitleRepository,
)
from src.application.use_cases import *
from src.core import settings


__all__ = [
    "AuthenticateUserUseCaseDep",
    "RegisterUserUseCaseDep",
    "AddUserTitleUseCaseDep",
    "UpdateUserTitleUseCaseDep",
    "GetTitleUseCaseDep",
]


async def get_auth_use_case(
    session: SessionDep,
    token_service: TokenServiceDep,
    hasher: PasswordHasherDep,
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        user_repository=UserRepository(session),
        token_service=token_service,
        password_hasher=hasher,
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


async def get_register_use_case(
    session: SessionDep,
    hasher: PasswordHasherDep,
    password_validator: PasswordValidatorDep,
    username_validator: UsernameValidatorDep,
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repository=UserRepository(session),
        password_hasher=hasher,
        password_validator=password_validator,
        username_validator=username_validator,
    )


async def get_add_user_title_use_case(
    session: SessionDep,
) -> AddUserTitleUseCase:
    return AddUserTitleUseCase(
        user_title_repository=UserTitleRepository(session),
        title_repository=TitleRepository(session),
    )


async def get_update_user_title_use_case(
    session: SessionDep,
) -> UpdateUserTitleUseCase:
    return UpdateUserTitleUseCase(
        user_title_repository=UserTitleRepository(session),
        title_repository=TitleRepository(session),
    )


async def get_title_use_case(
    session: SessionDep,
) -> GetTitleUseCase:
    return GetTitleUseCase(
        user_title_repository=UserTitleRepository(session),
        title_repository=TitleRepository(session),
    )


# === Dependencies Annotations ===
AuthenticateUserUseCaseDep = Annotated[
    AuthenticateUserUseCase,
    Depends(get_auth_use_case),
]
RegisterUserUseCaseDep = Annotated[
    RegisterUserUseCase,
    Depends(get_register_use_case),
]
AddUserTitleUseCaseDep = Annotated[
    AddUserTitleUseCase,
    Depends(get_add_user_title_use_case),
]
UpdateUserTitleUseCaseDep = Annotated[
    UpdateUserTitleUseCase,
    Depends(get_update_user_title_use_case),
]
GetTitleUseCaseDep = Annotated[
    GetTitleUseCase,
    Depends(get_title_use_case),
]
