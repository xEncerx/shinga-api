from src.domain.models.services.enums import ConsolidationStatus
from src.domain.models.titles import SourceTitleData, TitleData
from src.infrastructure.db.models import TitleRawDataDBModel
from .source_metadata_mapper import SourceMetadataMapper


class SourceTitleDataMapper:
    """Mapper for converting between SourceTitleData (domain) and TitleRawDataDBModel (database)."""

    @staticmethod
    def to_domain(db_model: TitleRawDataDBModel) -> SourceTitleData:
        """Convert TitleRawDataDBModel to SourceTitleData domain model."""
        source_metadata = SourceMetadataMapper.to_domain(db_model)
        title_data = TitleData.model_validate(db_model.raw_data)

        return SourceTitleData(
            source_metadata=source_metadata,
            title_data=title_data,
        )

    @staticmethod
    def to_db_dict(
        domain_model: SourceTitleData,
        consolidation_status: ConsolidationStatus = ConsolidationStatus.PENDING,
    ) -> dict:
        """
        Convert SourceTitleData to dictionary for TitleRawDataDBModel insert/update.
        Returns a dict that can be used for upsert operations.
        """
        metadata_dict = SourceMetadataMapper.to_db_dict(domain_model.source_metadata)

        return {
            **metadata_dict,
            "raw_data": domain_model.title_data.model_dump(mode="json"),
            "consolidation_status": consolidation_status,
        }
