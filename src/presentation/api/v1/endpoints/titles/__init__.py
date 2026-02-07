from fastapi import APIRouter

from .get_title import router as get_title_router

router = APIRouter(prefix="/titles")

router.include_router(get_title_router)
