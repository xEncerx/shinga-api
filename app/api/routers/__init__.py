from fastapi import APIRouter

from app.core import settings

from app.api.routers import (
    utils,
    users,
    titles,
)

api_routers = APIRouter(prefix=f"{settings.API_V1_STR}")
api_routers.include_router(utils.router)
api_routers.include_router(users.router)
api_routers.include_router(titles.router)
