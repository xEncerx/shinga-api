from fastapi import APIRouter

from src.presentation.api.schemas.responses import (
    TitleSearchResponse,
    TitleWithUserDataResponse,
    TitleResponse,
    UserTitleDataResponse,
    PaginationResponse,
    PaginationItemsResponse,
)
from src.presentation.api.dependencies.use_cases import SearchTitlesUseCaseDep
from src.presentation.api.schemas.requests import TitleSearchRequest
from src.presentation.api.dependencies import GetOptionalUserDep

router = APIRouter(prefix="/search", tags=["Search Titles"])


@router.post("")
async def search_titles_endpoint(
    request: TitleSearchRequest,
    user: GetOptionalUserDep,
    use_case: SearchTitlesUseCaseDep,
) -> TitleSearchResponse:
    result = await use_case.execute(
        query=request.query,
        type=request.type,
        status=request.status,
        genres=request.genres,  # type: ignore
        categories=request.categories,  # type: ignore
        min_rating=request.min_rating,
        max_rating=request.max_rating,
        min_chapters=request.min_chapters,
        max_chapters=request.max_chapters,
        bookmark=request.bookmark,
        user_id=user.id if user else None,
        sort_by=request.sort_by,
        order=request.order,
        page=request.page,
        page_size=request.page_size,
    )

    return TitleSearchResponse(
        pagination=PaginationResponse(
            last_visible_page=result.pagination.last_visible_page,
            has_next_page=result.pagination.has_next_page,
            current_page=result.pagination.current_page,
            items=PaginationItemsResponse(
                count=result.pagination.items.count,
                total=result.pagination.items.total,
                per_page=result.pagination.items.per_page,
            ),
        ),
        content=[
            TitleWithUserDataResponse(
                title=TitleResponse.from_domain(item.title),
                user_data=(
                    UserTitleDataResponse.from_domain(item.user_data)
                    if item.user_data
                    else None
                ),
            )
            for item in result.content
        ],
    )
