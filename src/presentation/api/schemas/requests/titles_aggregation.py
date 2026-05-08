from pydantic import BaseModel, Field, model_validator

__all__ = ["MergeTitlesRequest"]


class MergeTitlesRequest(BaseModel):
    major_id: int = Field(
        ...,
        ge=1,
        le=2147483647,
        description="Title to keep",
    )
    minor_id: int = Field(
        ...,
        ge=1,
        le=2147483647,
        description="Title to merge into the major title",
    )

    @model_validator(mode="after")
    def ids_must_differ(self) -> "MergeTitlesRequest":
        if self.major_id == self.minor_id:
            raise ValueError("major_id and minor_id must be different.")
        return self
