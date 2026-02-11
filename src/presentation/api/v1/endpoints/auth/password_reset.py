from fastapi import APIRouter

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
@map_domain_errors(
    {
        domain_errors.UserNotFoundError: api_errors.UserNotFound,
    }
)
async def request_password_reset_endpoint(
    request: RequestPasswordResetRequest,
    use_case: RequestPasswordResetUseCaseDep,
):
    """Request a password reset code to be sent to the user's email."""
    await use_case.execute(request.email, request.language)


@router.post("/verify", status_code=204)
@map_domain_errors(
    {
        domain_errors.VerificationCodeNotFoundError: api_errors.VerificationCodeNotFound,
        domain_errors.InvalidVerificationCodeError: api_errors.InvalidVerificationCode,
    }
)
async def verify_reset_code_endpoint(
    request: VerifyCodeRequest,
    use_case: VerifyPasswordResetCodeUseCaseDep,
):
    """Verify the provided password reset code for the given email."""
    await use_case.execute(request.email, request.code)


@router.post("/reset", status_code=204)
@map_domain_errors(
    {
        domain_errors.UserNotFoundError: api_errors.UserNotFound,
        domain_errors.ValidationError: api_errors.ValidationError,
        domain_errors.InvalidVerificationCodeError: api_errors.InvalidVerificationCode,
    }
)
async def reset_password_endpoint(
    request: ResetPasswordRequest,
    use_case: ResetPasswordUseCaseDep,
):
    """Reset the user's password using the provided email, verification code, and new password."""
    await use_case.execute(request.email, request.code, request.new_password)
