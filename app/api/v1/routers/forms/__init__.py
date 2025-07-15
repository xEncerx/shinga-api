from fastapi import APIRouter

from .titles import router as titles_router
from .user import router as user_router

router = APIRouter(prefix="/forms", tags=["forms"])
router.include_router(titles_router)
router.include_router(user_router)