from pydantic import BaseModel, EmailStr, Field

from .enums import UserRole


class UserData(BaseModel):
    id: int | None = Field(
        default=None, description="The unique identifier of the user."
    )

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="The unique username of the user.",
    )
    email: EmailStr
    hashed_password: str = Field(..., description="The hashed password of the user.")

    avatar_path: str | None = Field(
        default=None, description="The file path to the user's avatar image."
    )

    role: UserRole = Field(
        default=UserRole.USER, description="The role assigned to the user."
    )
    description: str | None = Field(
        default=None,
        min_length=4,
        max_length=600,
        description="A brief description or bio of the user.",
    )

    is_active: bool = Field(
        default=True,
        description="Indicates whether the user account is active.",
    )

    extended_data: dict | None = Field(
        default=None,
        description="Additional specific data that doesn't fit into predefined fields",
    )
