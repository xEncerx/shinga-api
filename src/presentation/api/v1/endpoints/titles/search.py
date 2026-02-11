from fastapi import APIRouter

from src.presentation.api.schemas.responses import (
    TitleSearchResponse,
    TitleWithUserDataResponse,
    TitleResponse,
    UserTitleDataResponse,
)
from src.presentation.api.dependencies.use_cases import SearchTitlesUseCaseDep
from src.presentation.api.schemas.requests import TitleSearchRequest
from src.presentation.api.dependencies import GetOptionalUserDep
from time import time

router = APIRouter(prefix="/search", tags=["Search Titles"])


@router.post("/")
async def search_titles_endpoint(
    request: TitleSearchRequest,
    user: GetOptionalUserDep,
    use_case: SearchTitlesUseCaseDep,
) -> TitleSearchResponse:
    start = time()
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
    end = time()
    print(f"Search titles executed in {end - start} seconds")

    return TitleSearchResponse(
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
        ]
    )
