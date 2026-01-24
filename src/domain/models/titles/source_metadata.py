from datetime import datetime, timezone
from pydantic import BaseModel, Field

from src.domain.models.source import Source

__all__ = ["SourceMetadata"]


class SourceMetadata(BaseModel):
    """Metadata about the source of title data."""

    source: Source = Field(description="Source of the title data")
    external_id: str = Field(description="ID of the title in the source system")
    source_url: str | None = Field(
        default=None,
        description="Direct URL to the title on the source",
    )
    is_deleted: bool = Field(
        default=False,
        description="Indicates if the title has been deleted or removed from the source",
    )
    loaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the data was loaded from the source",
    )
    extended_data: dict | None = Field(
        default=None,
        description="Additional source-specific data that doesn't fit into predefined fields",
    )
