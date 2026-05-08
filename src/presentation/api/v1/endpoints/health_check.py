from fastapi.responses import JSONResponse
from fastapi import APIRouter
import asyncio

from sqlmodel import text

from src.presentation.api.dependencies.database import SessionDep, get_redis_client

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/live")
async def liveness_check() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "alive"})


@router.get("/ready")
async def readiness_check(db_session: SessionDep) -> JSONResponse:
    redis = get_redis_client()

    async def check_redis():
        return await asyncio.wait_for(redis.ping(), timeout=2.0)  # type: ignore

    async def check_db():
        await asyncio.wait_for(db_session.execute(text("SELECT 1")), timeout=5.0)

    try:
        await asyncio.gather(check_redis(), check_db())
    except (asyncio.TimeoutError, Exception):
        return JSONResponse(status_code=503, content={"status": "unhealthy"})

    return JSONResponse(status_code=200, content={"status": "healthy"})
