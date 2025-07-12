from fastapi import APIRouter

from .me import router as me_router

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(me_router, prefix="/me")