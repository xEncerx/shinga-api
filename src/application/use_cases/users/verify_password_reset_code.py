from dataclasses import dataclass

from src.domain.errors import (
    InvalidVerificationCodeError,
    VerificationCodeNotFoundError,
)
from src.domain.interfaces import IVerificationCodeStorage


class VerifyPasswordResetCodeUseCase:
    """Use case for verifying password reset code"""

    def __init__(self, code_storage: IVerificationCodeStorage):
        """
        Initialize use case

        Args:
            code_storage: Storage for verification codes
        """
        self._code_storage = code_storage

    async def execute(self, email: str, code: str) -> None:
        """
        Verify the password reset code

        Args:
            email: User's email address
            code: Verification code to check

        Raises:
            VerificationCodeNotFoundError: If no code exists for email
            InvalidVerificationCodeError: If code doesn't match
        """
        # Check if code exists
        stored_code = await self._code_storage.get_code(email)

        if stored_code is None:
            raise VerificationCodeNotFoundError(
                f"No verification code found for {email}"
            )

        # Verify code matches
        if stored_code != code:
            raise InvalidVerificationCodeError("Invalid verification code")
