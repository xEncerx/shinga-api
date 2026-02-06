from pydantic import BaseModel, Field


__all__ = ["AccessTokenResponse"]


class AccessTokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of the token")
