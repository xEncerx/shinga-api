from fastapi import APIRouter, Request
import asyncio

from app.domain.models.exceptions import UserNotFoundError
from app.domain.use_cases import reset_user_password
from app.domain.services import EmailService
from app.api.v1.schemas import Message
from app.core.security import *
from ...schemas import *
from app.core import *

router = APIRouter(prefix="/password")


@router.post("/forgot")
@limiter.limit("2/minute;10/day")
async def forgot_password(
    forgot_form: ForgotPasswordForm,
    request: Request,
):
    """
    Sends a password reset code to the user's email.

    **Limits the request to 2 per minute and 10 per day.**

    Args:
        forgot_form (ForgotPasswordForm): Form containing the user's email.

    Returns:
        Message: Confirmation message indicating the reset code has been sent.

    Raises:
        EmailNotSent: If the email could not be sent.
    """
    email = forgot_form.email
    code = generate_code()

    await redis.setex(f"reset_code:{email}", settings.RESET_CODE_TTL, code)

    asyncio.create_task(
        EmailService.send_password_reset_email(
            recipient_email=email, reset_code=code
        )
    )

    return Message(message="Reset code sent to your email.")

@router.post("/verify-reset-code")
@limiter.limit("5/minute")
async def verify_reset_code(
    verify_form: VerifyResetCodeForm,
    request: Request,
):
    """
    Verifies the password reset code sent to the user's email.

    **Limits the request to 5 per minute.**

    Args:
        verify_form (VerifyResetCodeForm): Form containing the user's email and reset code.

    Returns:
        Message: Confirmation message indicating the reset code is valid.

    Raises:
        EmailNotSent: If the reset code is not found or has expired.
        EmailCodeMismatch: If the provided reset code does not match the stored code.
    """
    stored_code = await redis.get(f"reset_code:{verify_form.email}")

    if not stored_code:
        raise EmailNotSent(detail="Reset code not found or expired.")
    if stored_code.decode() != verify_form.code:
        raise EmailCodeMismatch(detail="Reset code does not match.")

    return Message(message="Reset code is valid.")

@router.post("/reset")
@limiter.limit("2/minute;10/day")
async def reset_password(
    restore_form: UserPasswordRestore,
    request: Request,
):
    """
    Resets the user's password using the provided reset code.

    **Limits the request to 2 per minute and 10 per day.**

    Args:
        restore_form (UserPasswordRestore): Form containing the user's email,
            reset code, and new password.
    Returns:
        Message: Confirmation message indicating the password has been reset.

    Raises:
        UserNotFound: If the user with the provided email does not exist.
        EmailNotSent: If the reset code is not found or has expired.
        EmailCodeMismatch: If the provided reset code does not match the stored code.
        PasswordTooWeak: If the new password does not meet strength requirements.
    """

    stored_code = await redis.get(f"reset_code:{restore_form.email}")

    if not stored_code:
        raise EmailNotSent(detail="Reset code not found or expired.")
    if stored_code.decode() != restore_form.code:
        raise EmailCodeMismatch(detail="Reset code does not match.")
    if not is_password_strong(restore_form.new_password):
        raise PasswordTooWeak()

    try:
        await redis.delete(f"reset_code:{restore_form.email}")
        await reset_user_password(
            email=restore_form.email,
            new_password=restore_form.new_password,
        )

        return Message(message="Password reset successfully.")
    except UserNotFoundError:
        raise UserNotFound()
