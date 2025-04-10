from fastapi import APIRouter

from app.models import Message

router = APIRouter(prefix=f"/utils", tags=["utils"])


@router.get("/ping")
async def ping() -> Message:
    """
    Test endpoint to check if the server is running.
    """
    return Message(message="pong!")
