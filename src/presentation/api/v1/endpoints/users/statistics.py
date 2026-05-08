from fastapi import APIRouter, Request

from src.presentation.api.dependencies import UserStatisticsUseCaseDep, GetUserDep
from src.presentation.api.schemas.responses.statistics import *
from src.presentation.api.dependencies.rate_limit import limiter

router = APIRouter(prefix="/statistics", tags=["User Statistics"])


@router.get("")
@limiter.limit("30/minute")
async def get_user_statistics_endpoint(
    user: GetUserDep,
    use_case: UserStatisticsUseCaseDep,
    request: Request,
) -> UserStatisticsResponse:
    """Endpoint to retrieve user statistics, including bookmarks and ratings."""
    result = await use_case.execute(user_id=user.id)  # type: ignore

    return UserStatisticsResponse(
        bookmarks=BookmarkStatisticsResponse(
            bookmarks=result.bookmarks.bookmarks,
            total=result.bookmarks.total,
        ),
        ratings=RatingStatisticsResponse(
            average_rating=result.ratings.average_rating,
            ratings_count=result.ratings.ratings_count,
            ratings_distribution=result.ratings.ratings_distribution,
        ),
    )
