from fastapi import APIRouter, Path

from src.presentation.api.dependencies import GetTitleUseCaseDep, GetOptionalUserDep
from src.presentation.api.decorators import map_domain_errors
from src.presentation.api.schemas import errors as api_errors
from src.presentation.api.schemas.responses.titles import *
from src.domain import errors as domain_errors

router = APIRouter(tags=["Get Titles"])


@router.get("/{title_id}")
@map_domain_errors(
    {
        domain_errors.RecordNotFoundError: api_errors.TitleNotFound,
    }
)
async def get_title_by_id_endpoint(
    title_id: int = Path(
        ...,
        ge=1,
        le=2147483647,  # Max value for 32-bit signed integer
    ),
    *,
    use_case: GetTitleUseCaseDep,
    user: GetOptionalUserDep,
) -> TitleDetailResponse:
    """
    Get title by ID with optional user-specific data.

    If user is authenticated, returns title data along with user's personal data
    (rating, bookmark status, etc.). Otherwise, returns only title data.
    """
    user_id = user.id if user else None
    result = await use_case.execute(title_id, user_id)

    # Convert domain models to response models
    title_response = TitleResponse.from_domain(result.title)
    user_data_response = (
        UserTitleDataResponse.from_domain(result.user_data)
        if result.user_data
        else None
    )

    return TitleDetailResponse(
        content=TitleWithUserDataResponse(
            title=title_response,
            user_data=user_data_response,
        )
    )
