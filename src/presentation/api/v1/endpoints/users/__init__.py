from fastapi import APIRouter

from .user_titles import router as user_titles_router
from .get_user import router as get_user_router
from .statistics import router as user_statistics_router

router = APIRouter(prefix="/users")

router.include_router(user_titles_router)
router.include_router(get_user_router)
router.include_router(user_statistics_router)
