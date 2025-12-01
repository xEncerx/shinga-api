from slowapi.util import get_remote_address
from slowapi import Limiter

from redis.asyncio import Redis

from .logging import setup_logging, logger
from .config import Settings

settings = Settings()  # type: ignore
limiter = Limiter(key_func=get_remote_address)
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD,
)


# === SENTRY INTEGRATION (OPTIONAL) ===
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.loguru import LoguruIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            CeleryIntegration(),
            LoguruIntegration(
                level=20,
                event_level=40,
            ),
        ],
        traces_sample_rate=0.1,
        release=getattr(settings, "VERSION", None),
        send_default_pii=False,
    )


def create_media_directories():
    from pathlib import Path

    Path(settings.MEDIA_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.COVER_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.AVATAR_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
