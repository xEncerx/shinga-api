from pydantic import BaseModel, EmailStr, Field

__all__ = ["SignUpRequest"]

class SignUpRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
