from pydantic import ValidationError as PydanticValidationError
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI

from src.presentation.api.v1.router import router as api_v1_router
from src.presentation.api.schemas.errors import BaseAPIException
from src.domain.models.settings import EnvFlavor
from src.presentation.api.middleware import *
from src.core import settings

app = FastAPI(
    debug=settings.FLAVOR == EnvFlavor.DEVELOPMENT,
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_exception_handler(BaseAPIException, base_api_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)  # type: ignore
app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)  # type: ignore

app.include_router(api_v1_router, prefix="/api")
