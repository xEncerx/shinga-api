from fastapi import APIRouter

from app.infrastructure.db.crud import *
from app.api.deps import CurrentUserDep
from app.api.v1.schemas import *


router = APIRouter()


@router.get("", response_model=UserPublic)
async def get_me(current_user: CurrentUserDep):
    """
    Get the current user's public profile information.
    """
    return UserPublic.model_validate(current_user.model_dump())


@router.patch("/update")
async def update_profile(
    user_data: UserUpdatableFields,
    *,
    current_user: CurrentUserDep,
) -> Message:
    """
    Update the current user's profile information.
    """
    if user_data.username is not None:
        is_available = await get_user(username=user_data.username) is None
        if not is_available:
            raise UserAlreadyExists(
                detail=f"Username is already taken",
            )
        
    data = user_data.model_dump(exclude_unset=True, exclude_none=True)
    if not data:
        raise ValidationError()

    result = await update_user_fields(
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
async def add_update_user_title(
    user_title_data: UserTitleUpdatableFields,
    *,
    current_user: CurrentUserDep,
) -> Message:
    is_title_exists = await get_title_by_id(id=user_title_data.title_id)
    if not is_title_exists:
        raise TitleNotFound(
            detail=f"Title with id '{user_title_data.title_id}' not found",
        )
    
    data = user_title_data.model_dump(exclude_none=True)
    if not data:
        raise ValidationError()
    
    result = await upsert_user_title(
        user_title=UserTitles(
            username=current_user.username,
            **data
        )
    )
    if result:
        return Message(message="User title updated successfully")
    else:
        raise UserRelatedError(
            detail="Failed to update user title. Please try again later.",
        )

@router.get("/titles")
async def read_user_titles(
    query: GetUserTitlesFields = GetUserTitlesFields(),
    *,
    current_user: CurrentUserDep,
) -> TitlePaginationResponse:
    user_data = await get_user_titles(
        username=current_user.username,
        page=query.page,
        per_page=query.per_page,
        bookmark=query.bookmark,
    )

    return TitlePaginationResponse(
        pagination=Pagination.model_validate(user_data["pagination"]),
        content=[
            TitleWithUserData(
                title=TitlePublic.model_validate(data["title"]),
                user_data=UserTitlePublic.model_validate(data["user_data"]) if data["user_data"] else None,
            ) for data in user_data["content"]
        ]
    )
