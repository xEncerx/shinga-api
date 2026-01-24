from pydantic import BaseModel, Field

from .source_metadata import SourceMetadata
from .title_data import TitleData

__all__ = ["SourceTitleData"]


class SourceTitleData(BaseModel):
    """Complete title information from a specific source, combining metadata and content."""

    # === Source metadata ===
    source_metadata: SourceMetadata = Field(
        description="Metadata about the source of the title data"
    )

    # === Title information ===
    title_data: TitleData = Field(
        description="Core title information as provided by the source"
    )
