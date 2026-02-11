from pydantic import BaseModel, EmailStr, Field

from src.domain.models import Language

__all__ = [
    "SignUpRequest",
    "RequestPasswordResetRequest",
    "VerifyCodeRequest",
    "ResetPasswordRequest",
]


class SignUpRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class RequestPasswordResetRequest(BaseModel):
    email: EmailStr
    language: Language = Language.EN


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str
