from fastapi import APIRouter

from src.presentation.api.dependencies import (
    GetUserDep,
    AddUserTitleUseCaseDep,
    UpdateUserTitleUseCaseDep,
)
from src.presentation.api.decorators import map_domain_errors
from src.domain.models.users import UserTitleData, UserTitleDataUpdate
from src.presentation.api.schemas import errors as api_errors
from src.domain import errors as domain_errors
from src.presentation.api.schemas.requests import (
    AddUserTitleRequest,
    UpdateUserTitleRequest,
)

router = APIRouter(tags=["User Titles"])


@router.put("/titles/{title_id}", status_code=204)
@map_domain_errors(
    {
        domain_errors.RecordNotFoundError: api_errors.TitleNotFound,
        domain_errors.RecordAlreadyExistsError: api_errors.UserTitleAlreadyExists,
    }
)
async def add_user_title_endpoint(
    title_id: int,
    request: AddUserTitleRequest,
    user: GetUserDep,
    use_case: AddUserTitleUseCaseDep,
):
    """
    Add a user's title data.
    """
    await use_case.execute(
        user_id=user.id,  # type: ignore
        title_id=title_id,
        data=UserTitleData(bookmark=request.bookmark),
    )


@router.patch("/titles/{title_id}", status_code=204)
@map_domain_errors(
    {
        domain_errors.RecordNotFoundError: api_errors.UserTitleNotFound,
    }
)
async def update_user_title_endpoint(
    title_id: int,
    request: UpdateUserTitleRequest,
    user: GetUserDep,
    use_case: UpdateUserTitleUseCaseDep,
):
    """
    Update a user's title data for the given title ID.
    Only the fields provided in the request will be updated; other fields will remain unchanged.
    """
    await use_case.execute(
        user_id=user.id,  # type: ignore
        title_id=title_id,
        data=UserTitleDataUpdate(
            rating=request.rating,
            current_url=str(request.current_url) if request.current_url else None,
            bookmark=request.bookmark,
            is_favorite=request.is_favorite,
            extended_data=None,
        ),
    )
