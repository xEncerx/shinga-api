from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from typing import AsyncGenerator
from fastapi import FastAPI
import uvicorn

from app.tasks import init_scheduler, scheduler
from app.api.routers import api_routers
from app.core import settings, limiter
from app.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    if settings.REDIS_URL:
        backend = RedisBackend(
            aioredis.from_url(settings.REDIS_URL),
        )
    else:
        backend = InMemoryBackend()

    FastAPICache.init(backend, prefix="api:cache")

    await init_db()
    init_scheduler()

    yield

    scheduler.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(api_routers)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

if __name__ == "__main__":
    uvicorn.run(app, log_config=None)
