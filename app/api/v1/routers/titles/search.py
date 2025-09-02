from fastapi import APIRouter, Request

from app.domain.use_cases import TitleSearchService, TitleSearchMode
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
    return await TitleSearchService.search(
        params=search_fields,
        username=current_user.username,
        mode=TitleSearchMode.GLOBAL,
    )
