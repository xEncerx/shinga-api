from pydantic_settings import BaseSettings, SettingsConfigDict
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import PostgresDsn, field_validator
from apscheduler.triggers.cron import CronTrigger
from slowapi.util import get_remote_address
from pydantic_core import MultiHostUrl
from datetime import timedelta
from slowapi import Limiter


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    API_V1_STR: str = "/api/v1"
    # = secrets.token_urlsafe(32)
    SECRET_KEY: str
    # 60 minutes * 24 hours * 30 days = 30 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    PROJECT_NAME: str = "Shinga - Manga Tracker"
    VERSION: str = "0.1.0"

    ALLOW_ORIGINS: list[str] | str = ["*"]
    ALLOW_METHODS: list[str] | str = ["*"]
    ALLOW_HEADERS: list[str] | str = ["*"]

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    REDIS_URL: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Logger
    FILE_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "logs/server.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 5

    # Task Scheduler
    BACKUP_TIME: CronTrigger = CronTrigger(hour=0, minute=0)
    BACKUP_DIR: str = "backups"
    PG_DUMP_PATH: str

    MANGA_UPDATER_INTERVAL: IntervalTrigger = IntervalTrigger(hours=10)
    MIN_UPDATE_INTERVAL: timedelta = timedelta(hours=5)

    @field_validator(
        "ALLOW_ORIGINS",
        "ALLOW_HEADERS",
        "ALLOW_METHODS",
        mode="before",
    )
    def parse_commas_str(cls, v: str) -> list[str]:
        if isinstance(v, str):
            if v.find(",") == -1:
                return [v.strip()]

            return [item.strip() for item in v.split(",")]
        elif isinstance(v, list):
            return v

        raise TypeError("ALLOW_* data must be a string separated by commas or a list")


settings = Settings()
limiter = Limiter(key_func=get_remote_address)
