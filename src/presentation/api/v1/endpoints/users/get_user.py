from fastapi import APIRouter, Request

from src.presentation.api.schemas.responses.users import UserResponse
from src.presentation.api.dependencies.rate_limit import limiter
from src.presentation.api.dependencies import GetUserDep

router = APIRouter(tags=["Get User"])


@router.get("/me")
@limiter.limit("45/minute")
async def get_me_endpoint(user: GetUserDep, request: Request) -> UserResponse:
    return UserResponse.from_domain(user)
