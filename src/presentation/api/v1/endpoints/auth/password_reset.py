from fastapi import APIRouter, Request

from src.presentation.api.dependencies.rate_limit import limiter
from src.presentation.api.schemas.requests import (
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    VerifyCodeRequest,
)
from src.presentation.api.dependencies.use_cases import (
    RequestPasswordResetUseCaseDep,
    ResetPasswordUseCaseDep,
    VerifyPasswordResetCodeUseCaseDep,
)
from src.presentation.api.decorators import map_domain_errors
from src.presentation.api.schemas import errors as api_errors
from src.domain import errors as domain_errors

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])


@router.post("/request", status_code=204)
@limiter.limit("5/minute")
@map_domain_errors(
    {
        domain_errors.UserNotFoundError: api_errors.UserNotFound,
    }
)
async def request_password_reset_endpoint(
    input: RequestPasswordResetRequest,
    use_case: RequestPasswordResetUseCaseDep,
    request: Request,
):
    """Request a password reset code to be sent to the user's email."""
    await use_case.execute(input.email, input.language)


@router.post("/verify", status_code=204)
@limiter.limit("15/minute")
@map_domain_errors(
    {
        domain_errors.VerificationCodeNotFoundError: api_errors.VerificationCodeNotFound,
        domain_errors.InvalidVerificationCodeError: api_errors.InvalidVerificationCode,
    }
)
async def verify_reset_code_endpoint(
    input: VerifyCodeRequest,
    use_case: VerifyPasswordResetCodeUseCaseDep,
    request: Request,
):
    """Verify the provided password reset code for the given email."""
    await use_case.execute(input.email, input.code)


@router.post("/reset", status_code=204)
@limiter.limit("5/minute")
@map_domain_errors(
    {
        domain_errors.UserNotFoundError: api_errors.UserNotFound,
        domain_errors.ValidationError: api_errors.ValidationError,
        domain_errors.InvalidVerificationCodeError: api_errors.InvalidVerificationCode,
    }
)
async def reset_password_endpoint(
    input: ResetPasswordRequest,
    use_case: ResetPasswordUseCaseDep,
    request: Request,
):
    """Reset the user's password using the provided email, verification code, and new password."""
    await use_case.execute(input.email, input.code, input.new_password)
