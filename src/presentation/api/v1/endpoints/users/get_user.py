from fastapi import APIRouter

from src.presentation.api.schemas.responses.users import UserResponse
from src.presentation.api.dependencies import GetUserDep, SessionDep
from src.infrastructure.db.repositories import UserRepository
from src.presentation.api.schemas.errors import UserNotFound

router = APIRouter(tags=["Get User"])


@router.get("/me")
async def get_me_endpoint(user: GetUserDep, session: SessionDep):
    repo = UserRepository(session)
    user_data = await repo.get_by_id(user.id)  # type: ignore

    if not user_data:
        raise UserNotFound()

    return UserResponse.from_domain(user_data)
