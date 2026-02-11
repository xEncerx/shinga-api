from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from src.infrastructure.security import (
    PasswordValidator,
    UsernameValidator,
    BcryptPasswordHasher,
    JWTService,
)
from src.infrastructure.storage import RedisVerificationCodeStorage
from src.infrastructure.localization import LocalizationService
from src.infrastructure.email import EmailTemplateRenderer
from src.domain.services import TextNormalizer
from src.domain.interfaces import *
from .database import RedisDep
from src.core import settings

__all__ = [
    "PasswordHasherDep",
    "PasswordValidatorDep",
    "UsernameValidatorDep",
    "TokenServiceDep",
    "TextNormalizerDep",
    "TemplateRendererDep",
    "VerificationStorageDep",
    "LocalizationServiceDep",
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


@lru_cache(1)
def get_template_renderer() -> IEmailTemplateRenderer:
    return EmailTemplateRenderer(templates_directory=settings.EMAIL_TEMPLATES_DIR)


@lru_cache(1)
def get_verification_storage(redis_client: RedisDep) -> IVerificationCodeStorage:
    return RedisVerificationCodeStorage(redis_client)


@lru_cache(1)
def get_localization_service() -> ILocalizationService:
    return LocalizationService()


# === Dependencies Annotations ===
PasswordHasherDep = Annotated[IPasswordHasher, Depends(get_password_hasher)]
PasswordValidatorDep = Annotated[IDataValidator, Depends(get_password_validator)]
UsernameValidatorDep = Annotated[IDataValidator, Depends(get_username_validator)]
TokenServiceDep = Annotated[ITokenService, Depends(get_token_service)]
TextNormalizerDep = Annotated[TextNormalizer, Depends(get_text_normalizer)]
TemplateRendererDep = Annotated[EmailTemplateRenderer, Depends(get_template_renderer)]
VerificationStorageDep = Annotated[
    RedisVerificationCodeStorage, Depends(get_verification_storage)
]
LocalizationServiceDep = Annotated[
    LocalizationService, Depends(get_localization_service)
]
