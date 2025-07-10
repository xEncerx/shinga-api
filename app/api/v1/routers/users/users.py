from fastapi import APIRouter

from app.api.v1.schemas.user import UserPublic
from app.api.deps import CurrentUserDep

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: CurrentUserDep):
    return UserPublic.model_validate(current_user)
