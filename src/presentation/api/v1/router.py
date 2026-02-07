from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.forms import router as forms_router
from .endpoints.users import router as users_router
from .endpoints.titles import router as titles_router

__all__ = ["router"]

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(forms_router)
router.include_router(users_router)
router.include_router(titles_router)
