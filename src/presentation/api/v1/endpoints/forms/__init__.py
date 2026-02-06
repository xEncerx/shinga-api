from fastapi import APIRouter

from .titles import router as titles_router

router = APIRouter(prefix="/forms")

router.include_router(titles_router)
