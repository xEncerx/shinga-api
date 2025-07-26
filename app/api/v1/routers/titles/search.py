from fastapi import APIRouter, Request

from app.infrastructure.db.crud.title import *
from app.api.deps import CurrentUserDep
from app.core import limiter
from ...schemas import *

router = APIRouter()


@router.get("/search")
@limiter.limit("60/minute")
async def global_search(
    search_fields: TitleSearchFields,
    current_user: CurrentUserDep,
    request: Request,
) -> TitlePaginationResponse:
    """
    Search for titles with various filters and sorting options.

    **Limits the request to 60 per minute.**
    """
    search_params = search_fields.model_dump()
    if search_params.get("genres"):
        search_params["genres"] = [
            genre
            for name in set(search_params["genres"])
            if (genre := TitleGenre.get(en=name, ru=name))
        ] or None

    titles = await TitleCRUD.read.search(
        **search_params,
        username=current_user.username,
    )

    return TitlePaginationResponse(
        pagination=Pagination.model_validate(titles["pagination"]),
        content=[
            TitleWithUserData(
                title=TitlePublic.model_validate(data["title"]),
                user_data=(
                    UserTitlePublic.model_validate(data["user_data"])
                    if data["user_data"]
                    else None
                ),
            )
            for data in titles["content"]
        ],
    )
