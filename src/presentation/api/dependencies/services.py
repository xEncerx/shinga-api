from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from src.infrastructure.security import (
    PasswordValidator,
    UsernameValidator,
    BcryptPasswordHasher,
    JWTService,
)
from src.domain.interfaces import IPasswordHasher, IDataValidator, ITokenService
from src.domain.services import TextNormalizer
from src.core import settings

__all__ = [
    "PasswordHasherDep",
    "PasswordValidatorDep",
    "UsernameValidatorDep",
    "TokenServiceDep",
    "TextNormalizerDep",
]


@lru_cache(1)
def get_password_hasher() -> IPasswordHasher:
    return BcryptPasswordHasher()


@lru_cache(1)
def get_password_validator() -> IDataValidator:
    return PasswordValidator(require_special_char=False)


@lru_cache(1)
def get_username_validator() -> IDataValidator:
    return UsernameValidator()


@lru_cache(1)
def get_token_service() -> ITokenService:
    return JWTService(settings.SECRET_KEY, settings.ALGORITHM)


@lru_cache(1)
def get_text_normalizer() -> TextNormalizer:
    return TextNormalizer()


# === Dependencies Annotations ===
PasswordHasherDep = Annotated[IPasswordHasher, Depends(get_password_hasher)]
PasswordValidatorDep = Annotated[IDataValidator, Depends(get_password_validator)]
UsernameValidatorDep = Annotated[IDataValidator, Depends(get_username_validator)]
TokenServiceDep = Annotated[ITokenService, Depends(get_token_service)]
TextNormalizerDep = Annotated[TextNormalizer, Depends(get_text_normalizer)]
