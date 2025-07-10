from .yandex_oauth import router as yandex_oauth_router
from .login import router as login_router
from .signup import router as signup_router

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(yandex_oauth_router)
router.include_router(login_router)
router.include_router(signup_router)