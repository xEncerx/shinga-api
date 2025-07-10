from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from datetime import timedelta
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    API_URL: str = "http://localhost:8000"
    API_V1_STR: str = "/api/v1"

    # Project settings
    PROJECT_NAME: str = "Shinga Api"
    VERSION: str = "0.2.0"

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    # OAuth settings
    # --- YANDEX ---
    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_REDIRECT_URI: str = f"{API_URL}{API_V1_STR}/auth/yandex/callback"
    # --- GOOGLE ---

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # SMTP settings
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

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

    # Media settings
    COVER_STORAGE_PATH: str = "app/api/media/covers"
    COVER_PUBLIC_PATH: str = "/media/covers"
    COVER_404_PATH: str = "/media/covers/404.webp"
    DEFAULT_AVATAR_PATH: str = "/media/avatars/default.webp"

    # OpenAI API settings
    OPENAI_API_BASE: str
    OPENAI_API_MODEL: str

    # Proxy settings
    PROXY_FETCH_INTERVAL: int = 3600  # 1 hour
    PROXY_VALIDATION_INTERVAL: int = 1800  # 30 minutes
    PROXY_SOURCES: list[str] | None = None

    # Rate limiting
    PROXY_RPS_LIMIT: int = 3
    PROXY_RPM_LIMIT: int = 60

    # Global Title Parser settings
    QUEUE_UPDATE_INTERVAL: int = 600  # seconds
    GTP_UPDATE_INTERVAL: timedelta = timedelta(days=1)

    # PATH
    TEMP_PATH: Path = Path(__file__).parent.parent.parent / "temp"
    CORE_PATH: Path = Path(__file__).parent
