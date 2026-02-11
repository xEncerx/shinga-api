from pydantic import BaseModel, Field

from src.domain.models import UserRole, UserData

__all__ = ["UserResponse"]


class UserResponse(BaseModel):
    id: int | None = Field(
        default=None, description="The unique identifier of the user."
    )

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="The unique username of the user.",
    )
    email: str = Field(..., description="The email address of the user.")

    avatar_path: str = Field(description="The file path to the user's avatar image.")

    role: UserRole = Field(
        default=UserRole.USER, description="The role assigned to the user."
    )
    description: str | None = Field(
        default=None,
        min_length=4,
        max_length=600,
        description="A brief description or bio of the user.",
    )

    @classmethod
    def from_domain(cls, user: UserData) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            avatar_path=user.avatar_path,
            role=user.role,
            description=user.description,
        )
