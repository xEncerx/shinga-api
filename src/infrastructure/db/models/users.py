from sqlmodel import SQLModel, Field, Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLEnum
from pydantic import EmailStr

from src.domain.models.users import UserRole


class UserDBModel(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    username: str = Field(
        index=True,
        ge=3,
        le=30,
        unique=True,
        description="Unique username for the user",
    )
    email: EmailStr = Field(index=True, unique=True, description="User's email address")

    hashed_password: str = Field(description="Hashed password for authentication")

    # OAuth providers
    google_id: str | None = Field(default=None, index=True)
    yandex_id: str | None = Field(default=None, index=True)

    role: UserRole = Field(
        sa_column=Column(SQLEnum(UserRole)),
        default=UserRole.USER,
        description="Role assigned to the user",
    )
    avatar_path: str | None = Field(
        default=None,
        description="File path to the user's avatar image",
    )
    description: str | None = Field(
        default=None,
        ge=4,
        le=600,
        description="Brief description or bio of the user",
    )
    is_active: bool = Field(
        default=True,
        description="Indicates whether the user account is active",
    )

    extended_data: dict | None = Field(
        default=None,
        sa_column=Column(
            JSONB,
            nullable=True,
        ),
        description="Additional data that doesn't fit into predefined fields",
    )

    registration_date: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )
