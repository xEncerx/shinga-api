from pydantic import BaseModel, Field
from typing import Generic, TypeVar

__all__ = ["BaseContentResponse"]

T = TypeVar("T")


class BaseContentResponse(BaseModel, Generic[T]):
    """Base response model for content-related endpoints."""

    content: T = Field(
        ...,
        description="Content data with dynamic structure depending on the endpoint",
    )
