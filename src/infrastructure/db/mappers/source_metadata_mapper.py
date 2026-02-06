from src.infrastructure.db.models import TitleRawDataDBModel
from src.domain.models.titles import SourceMetadata


class SourceMetadataMapper:
    """Mapper for converting between SourceMetadata (domain) and TitleRawDataDBModel fields."""

    @staticmethod
    def to_domain(db_model: TitleRawDataDBModel) -> SourceMetadata:
        """Extract SourceMetadata from TitleRawDataDBModel."""
        return SourceMetadata(
            source=db_model.source,
            external_id=db_model.external_id,
            source_url=db_model.source_url,
            is_deleted=db_model.is_deleted,
            loaded_at=db_model.fetched_at,
            extended_data=db_model.extended_data,
        )

    @staticmethod
    def to_db_dict(domain_model: SourceMetadata) -> dict:
        """
        Convert SourceMetadata to dictionary of TitleRawDataDBModel fields.
        Returns a dict that can be used for insert/update operations.
        """
        return {
            "source": domain_model.source,
            "external_id": domain_model.external_id,
            "source_url": domain_model.source_url,
            "is_deleted": domain_model.is_deleted,
            "extended_data": domain_model.extended_data or {},
        }
