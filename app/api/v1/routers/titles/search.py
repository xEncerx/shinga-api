from fastapi import APIRouter, Query, Request

from app.infrastructure.db.crud.title import *
from app.api.deps import CurrentUserDep
from app.core import limiter
from ...schemas import *

router = APIRouter()


@router.get("/global-search")
@limiter.limit("60/minute")
async def global_search(
    query: str,
    limit: int = Query(default=10, ge=1, le=50),
    *,
    current_user: CurrentUserDep,
    request: Request
) -> TitleSearchResponse:
    """
    Global search for titles by name with user-specific data.

    **Limits the request to 60 per minute.**
    """

    titles = await TitleCRUD.read.by_name(
        query,
        limit=limit,
        username=current_user.username,
    )

    content = []
    for title in titles:
        title_data = TitlePublic.model_validate(title["title"])
        user_data = (
            UserTitlePublic.model_validate(title["user_data"])
            if title["user_data"]
            else None
        )

        content.append(
            TitleWithUserData(
                title=title_data,
                user_data=user_data,
            )
        )
    return TitleSearchResponse(content=content)
