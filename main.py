from slowapi.errors import RateLimitExceeded

from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
import uvicorn

from app.api import *
from app.core import *


async def lifespan(app: FastAPI):
    # Initialize any resources needed for the app
    create_media_directories()
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    # Covers static files. Better to use nginx or other web server for production.
    # ! Will be removed in future releases.
    app.mount(
        "/media/covers",
        StaticFiles(directory=settings.COVER_STORAGE_PATH),
        name="covers",
    )
    app.mount(
        "/media/avatars",
        StaticFiles(directory=settings.AVATAR_STORAGE_PATH),
        name="avatars",
    )
    yield
    # Cleanup resources when the app is shutting down
    await redis.close()


app = FastAPI(
    lifespan=lifespan,  # type: ignore
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)
app.include_router(router)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, slowapi_exception_handler)  # type: ignore
app.add_exception_handler(HTTPException, exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, pydantic_exception_handler)  # type: ignore


if __name__ == "__main__":
    setup_logging()
    uvicorn.run(app, log_config=None)
