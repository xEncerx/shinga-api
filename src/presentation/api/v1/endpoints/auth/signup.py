from fastapi import APIRouter, Request

from src.presentation.api.dependencies.use_cases import RegisterUserUseCaseDep
from src.presentation.api.schemas.requests import SignUpRequest
from src.presentation.api.decorators import map_domain_errors
from src.presentation.api.schemas import errors as api_errors
from src.presentation.api.dependencies.rate_limit import limiter
from src.domain import errors as domain_errors

router = APIRouter(prefix="/signup", tags=["Registration"])


@router.post("", status_code=204)
@limiter.limit("5/minute")
@map_domain_errors(
    {
        domain_errors.ValidationError: api_errors.ValidationError,
        domain_errors.UserAlreadyExistsError: api_errors.UserAlreadyExists,
    }
)
async def signup_endpoint(
    input: SignUpRequest,
    use_case: RegisterUserUseCaseDep,
    request: Request,
) -> None:
    """
    Register a new user with username, email, and password

    Request Body:
    - **username**: Desired username for the new user
    - **email**: Email address of the new user
    - **password**: Password for the new user account
    """
    await use_case.execute(
        username=input.username,
        email=input.email,
        password=input.password,
    )
