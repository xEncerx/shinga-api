from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Annotated

from app.infrastructure.storage import MediaManger
from app.core import limiter, settings, logger
from app.infrastructure.db.crud import *
from app.api.deps import CurrentUserDep
from app.api.v1.schemas import *


router = APIRouter(prefix="/file")


@router.put("/avatar")
@limiter.limit("1/second;30/minute")
async def upload_avatar(
    current_user: CurrentUserDep,
    avatar: Annotated[UploadFile, File()],
    request: Request,
) -> JSONResponse:
    """
    Upload a new avatar for the current user.

    **Limits: 1 request per second, 30 requests per minute.**
    """

    if avatar.size > settings.MAX_AVATAR_SIZE:  # 2 MB limit # type: ignore
        raise FileTooLarge()

    file_ext = avatar.filename.split(".")[-1].lower()  # type: ignore
    if file_ext not in settings.ALLOWED_AVATAR_EXTENSIONS:
        raise FileExtensionNotAllowed()

    try:
        async with MediaManger() as media_manager:
            avatar_path = await media_manager.save_avatar(avatar, current_user.id)  # type: ignore

        if not avatar_path:
            raise FileRelatedError(detail="Failed to save avatar. Try again later.")

        await UserCRUD.update.fields(
            user_id=current_user.id,  # type: ignore
            avatar=avatar_path,
        )

        return JSONResponse(
            content={
                "message": "Avatar uploaded successfully",
                "avatar": avatar_path,
            }
        )
    except Exception as e:
        logger.error(f"Failed to save avatar: {str(e)}")
        raise FileRelatedError(detail="Failed to save avatar. Try again later.")
