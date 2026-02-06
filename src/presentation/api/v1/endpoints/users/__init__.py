from fastapi import APIRouter

from .user_titles import router as user_titles_router

router = APIRouter(prefix="/users")

router.include_router(user_titles_router)
