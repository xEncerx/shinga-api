from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .titles import router as titles_router
from .upload_file import router as upload_file_router

from app.core import settings

router = APIRouter(prefix=settings.API_V1_STR)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(titles_router)
router.include_router(upload_file_router, prefix="/upload", tags=["upload"])