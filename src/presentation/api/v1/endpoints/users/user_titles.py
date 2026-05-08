from fastapi import APIRouter, Path, Request

from src.presentation.api.dependencies import (
    GetUserDep,
    AddUserTitleUseCaseDep,
    UpdateUserTitleUseCaseDep,
)
from src.presentation.api.decorators import map_domain_errors
from src.domain.models.users import UserTitleData, UserTitleDataUpdate
from src.presentation.api.schemas import errors as api_errors
from src.presentation.api.dependencies.rate_limit import limiter
from src.domain import errors as domain_errors
from src.presentation.api.schemas.requests import (
    AddUserTitleRequest,
    UpdateUserTitleRequest,
)

router = APIRouter(tags=["User Titles"])


@router.put("/titles/{title_id}", status_code=204)
@limiter.limit("45/minute")
@map_domain_errors(
    {
        domain_errors.RecordNotFoundError: api_errors.TitleNotFound,
        domain_errors.RecordAlreadyExistsError: api_errors.UserTitleAlreadyExists,
    }
)
async def add_user_title_endpoint(
    title_id: int = Path(..., ge=1),
    *,
    input: AddUserTitleRequest,
    user: GetUserDep,
    use_case: AddUserTitleUseCaseDep,
    request: Request,
):
    """
    Add a user's title data.
    """
    await use_case.execute(
        user_id=user.id,  # type: ignore
        title_id=title_id,
        data=UserTitleData(bookmark=input.bookmark),
    )


@router.patch("/titles/{title_id}", status_code=204)
@limiter.limit("45/minute")
@map_domain_errors(
    {
        domain_errors.RecordNotFoundError: api_errors.UserTitleNotFound,
    }
)
async def update_user_title_endpoint(
    title_id: int = Path(..., ge=1),
    *,
    input: UpdateUserTitleRequest,
    user: GetUserDep,
    use_case: UpdateUserTitleUseCaseDep,
    request: Request,
):
    """
    Update a user's title data for the given title ID.
    Only the fields provided in the request will be updated; other fields will remain unchanged.
    """
    await use_case.execute(
        user_id=user.id,  # type: ignore
        title_id=title_id,
        data=UserTitleDataUpdate(
            rating=input.rating,
            current_url=str(input.current_url) if input.current_url else None,
            bookmark=input.bookmark,
            is_favorite=input.is_favorite,
            note=input.note,
            extended_data=None,
        ),
    )
