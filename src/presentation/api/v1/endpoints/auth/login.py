from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, Request
from typing import Annotated

from src.presentation.api.dependencies.use_cases import AuthenticateUserUseCaseDep
from src.presentation.api.schemas.responses.auth import AccessTokenResponse
from src.presentation.api.decorators import map_domain_errors
from src.presentation.api.schemas import errors as api_errors
from src.presentation.api.dependencies.rate_limit import limiter
from src.domain import errors as domain_errors

router = APIRouter(prefix="/login", tags=["Login"])


@router.post("/access-token")
@limiter.limit("5/minute")
@map_domain_errors(
    {
        domain_errors.MissingCredentialsError: api_errors.MissingCredentials,
        domain_errors.InvalidCredentialsError: api_errors.InvalidCredentials,
    }
)
async def login_access_token_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: AuthenticateUserUseCaseDep,
    request: Request,
) -> AccessTokenResponse:
    """
    Login to get access token for authorized requests

    Request Body Form Data:
    - **username**: Username or Email of the user
    - **password**: User's password
    """
    username = form_data.username if "@" not in form_data.username else None
    email = form_data.username if "@" in form_data.username else None
    password = form_data.password

    result = await use_case.execute(
        username=username,
        email=email,
        plain_password=password,
    )

    return AccessTokenResponse(
        access_token=result.access_token,
        token_type=result.token_type,
    )
