from fastapi_cache.decorator import cache

from fastapi import APIRouter, Request

from app.domain.use_cases import TitleSearchService, TitleSearchMode
from app.api.deps import CurrentUserDep
from app.core import limiter
from ...schemas import *

router = APIRouter()


@router.post("/search")
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
        user_id=current_user.id,
        mode=TitleSearchMode.GLOBAL,
    )


@router.get("/{title_id}")
@limiter.limit("60/minute")
@cache(expire=60 * 30)
async def get_title_data(
    title_id: str,
    *,
    request: Request,
) -> TitleSearchResponse:
    """
    Get detailed information about a specific title.

    **Limits the request to 60 per minute.**
    """
    response = await TitleSearchService.get_title_by_id(title_id)
    if not response:
        raise TitleNotFound(detail=f"Title with ID: <{title_id}> not found.")

    return TitleSearchResponse(content=[response])


@router.get("/{title_id}/recommendations")
@limiter.limit("60/minute")
async def get_title_recommendations(
    title_id: str,
    *,
    current_user: CurrentUserDep,
    request: Request,
) -> TitleSearchResponse:
    """
    Get recommendations for a specific title.

    **Limits the request to 60 per minute.**
    """
    return await TitleSearchService.get_recommendations(
        title_id,
        user_id=current_user.id,
    )
