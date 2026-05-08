from fastapi import APIRouter, Request

from src.presentation.api.dependencies.rate_limit import limiter
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
@limiter.limit("45/minute")
async def search_titles_endpoint(
    input: TitleSearchRequest,
    user: GetOptionalUserDep,
    use_case: SearchTitlesUseCaseDep,
    request: Request,
) -> TitleSearchResponse:
    result = await use_case.execute(
        query=input.query,
        type=input.type,
        status=input.status,
        genres=input.genres,  # type: ignore
        categories=input.categories,  # type: ignore
        min_rating=input.min_rating,
        max_rating=input.max_rating,
        min_chapters=input.min_chapters,
        max_chapters=input.max_chapters,
        bookmark=input.bookmark,
        user_id=user.id if user else None,
        sort_by=input.sort_by,
        sort_order=input.sort_order,
        page=input.page,
        page_size=input.page_size,
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
