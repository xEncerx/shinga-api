from fastapi import APIRouter, Request

from app.domain.use_cases import TitleSearchService, TitleSearchMode
from app.infrastructure.db.crud import *
from app.api.deps import CurrentUserDep
from app.api.v1.schemas import *
from app.core import limiter


router = APIRouter()


@router.get("", response_model=UserPublic)
@limiter.limit("3/second;60/minute")
async def get_me(
    current_user: CurrentUserDep,
    request: Request,
):
    """
    Get the current user's public profile information.

    **Limits: 3 requests per second, 60 requests per minute.**
    """
    return UserPublic.model_validate(current_user.model_dump())


@router.patch("/update")
@limiter.limit("1/second;30/minute")
async def update_profile(
    user_data: UserUpdatableFields,
    *,
    current_user: CurrentUserDep,
    request: Request,
) -> Message:
    """
    Update the current user's profile information.

    **Limits: 1 requests per second, 30 requests per minute.**
    """
    if user_data.username is not None:
        is_available = await UserCRUD.read.user(username=user_data.username) is None
        if not is_available:
            raise UserAlreadyExists(
                detail=f"Username is already taken",
            )

    data = user_data.model_dump(exclude_unset=True, exclude_none=True)
    if not data:
        raise ValidationError()

    result = await UserCRUD.update.fields(
        user_id=current_user.id,  # type: ignore
        **data,
    )
    if result:
        return Message(message="Profile updated successfully")
    else:
        raise UserRelatedError(
            detail="Failed to update profile. Please try again later.",
        )


@router.put("/titles/update")
@limiter.limit("1/second;30/minute")
async def upsert_user_title(
    user_title_data: UserTitleUpdatableFields,
    *,
    current_user: CurrentUserDep,
    request: Request,
) -> Message:
    """
    Add or update the user's title.

    **Limits: 1 requests per second, 30 requests per minute.**
    """
    is_title_exists = await TitleCRUD.read.by_id(id=user_title_data.title_id)
    if not is_title_exists:
        raise TitleNotFound(
            detail=f"Title with id '{user_title_data.title_id}' not found",
        )

    data = user_title_data.model_dump(exclude_none=True)
    if not data:
        raise ValidationError()

    result = await UserCRUD.create.user_title(
        user_title=UserTitles(username=current_user.username, **data)
    )
    if result:
        return Message(message="User title updated successfully")
    else:
        raise UserRelatedError(
            detail="Failed to update user title. Please try again later.",
        )


@router.get("/votes")
@limiter.limit("3/second;60/minute")
async def get_user_votes(
    *,
    current_user: CurrentUserDep,
    request: Request,
) -> UserVotes:
    """
    Get the current user's voting statistics.

    **Limits: 3 requests per second, 60 requests per minute.**
    """
    return await UserCRUD.read.votes(username=current_user.username)


@router.get("/titles")
@limiter.limit("3/second;60/minute")
async def get_user_titles(
    search_fields: TitleSearchFields,
    current_user: CurrentUserDep,
    request: Request,
) -> TitlePaginationResponse:
    """
    Get the current user's titles with pagination.

    **Limits: 3 requests per second, 60 requests per minute.**
    """
    return await TitleSearchService.search(
        params=search_fields,
        username=current_user.username,
        mode=TitleSearchMode.USER_ONLY,
    )
