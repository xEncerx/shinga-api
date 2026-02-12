from pydantic import ValidationError as PydanticValidationError
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI

from src.presentation.api.v1.endpoints.health_check import router as health_check_router
from src.presentation.api.dependencies.database import get_redis_client
from src.presentation.api.v1.router import router as api_v1_router
from src.presentation.api.schemas.errors import BaseAPIException
from src.infrastructure.tasks import email_broker
from src.domain.models.settings import EnvFlavor
from src.presentation.api.middleware import *
from src.core import settings


async def lifespan(_: FastAPI):
    # Initialize any resources needed for the app
    redis = get_redis_client()
    await redis.ping()  # type: ignore

    # Startup task brokers
    await email_broker.startup()

    yield
    # Cleanup resources when the app is shutting down
    await redis.aclose()


app = FastAPI(
    debug=settings.FLAVOR == EnvFlavor.DEVELOPMENT,
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,  # type: ignore
)


app.add_exception_handler(BaseAPIException, base_api_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)  # type: ignore
app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)  # type: ignore

app.include_router(api_v1_router, prefix="/api")
app.include_router(health_check_router)
