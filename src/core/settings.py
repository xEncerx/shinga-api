from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl

from src.domain.models.settings import EnvFlavor

__all__ = ["settings"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    FLAVOR: EnvFlavor = EnvFlavor.DEVELOPMENT

    # Application metadata
    APP_NAME: str = "Shinga"
    APP_VERSION: str = "0.1.1"

    # Api settings
    API_URL: str = "http://localhost:8000"

    # Network settings
    PROXY: str | None = None

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int = 6379

    # Email settings (SMTP)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_DOMAIN: str
    SMTP_USE_TLS: bool = True
    # Verification code settings
    VERIFICATION_CODE_EXPIRATION_MINUTES: int = 15
    # Email templates
    EMAIL_TEMPLATES_DIR: str = "templates/email"

    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    ALGORITHM: str = "HS256"

    # Storage settings
    STORAGE_BASE_PATH: str = "storage/"
    COVER_STORAGE_FOLDER: str = "covers/"
    COVER_PUBLIC_URL: str = "/static/covers/"

    PENDING_COVER_URL: str = "/static/covers/pending.webp"
    DEFAULT_AVATAR_URL: str = "/static/avatars/default.webp"

    # Cover processing settings
    COVER_VARIANTS: dict[str, tuple[int, int]] = {
        "thumbnail": (150, 225),
        "original": (300, 450),
    }
    IMAGE_QUALITY: int = 95
    BASE_IMAGE_FORMAT: str = "webp"

    # === Utility properties ===
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @property
    def REDIS_DSN(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
        )


settings = Settings()  # type: ignore
