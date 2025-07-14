from slowapi.util import get_remote_address
from slowapi import Limiter

from redis.asyncio import Redis

from .logging import setup_logging, logger
from .config import Settings
from .enums import *

settings = Settings() # type: ignore
limiter = Limiter(key_func=get_remote_address)
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD,
)

def create_media_directories():
    from pathlib import Path

    Path(settings.MEDIA_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.COVER_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.AVATAR_STORAGE_PATH).mkdir(parents=True, exist_ok=True)