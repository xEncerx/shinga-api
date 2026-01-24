from pydantic import BaseModel, Field

from src.domain.models.source import Source


class SourceDetail(BaseModel):
    source: Source = Field(description="Source of the title data")

    # === Pagination Details ===
    total_pages: int = Field(
        description="Total number of pages available from the source"
    )
    items_per_page: int = Field(
        description="Number of items per page provided by the source"
    )
