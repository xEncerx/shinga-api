from fastapi import APIRouter

from src.core import settings

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/")
async def health_check_endpoint():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
