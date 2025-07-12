from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
import uvicorn

from app.api import router, exception_handler
from app.core import *


async def lifespan(app: FastAPI):
    # Initialize any resources needed for the app
    yield
    # Cleanup resources when the app is shutting down
    await redis.close()


app = FastAPI()
app.include_router(router)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
app.add_exception_handler(HTTPException, exception_handler)  # type: ignore

# Covers static files. Better to use nginx or other web server for production.
app.mount(
    "/media/covers", StaticFiles(directory=settings.COVER_STORAGE_PATH), name="covers"
)
app.mount(
    "/media/avatars", StaticFiles(directory=settings.AVATAR_STORAGE_PATH), name="avatars"
)


if __name__ == "__main__":
    setup_logging()
    uvicorn.run(app, log_config=None)
