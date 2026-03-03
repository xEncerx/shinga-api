from fastapi import APIRouter

from src.presentation.api.schemas.responses.users import UserResponse
from src.presentation.api.dependencies import GetUserDep

router = APIRouter(tags=["Get User"])


@router.get("/me")
async def get_me_endpoint(user: GetUserDep):
    return UserResponse.from_domain(user)
