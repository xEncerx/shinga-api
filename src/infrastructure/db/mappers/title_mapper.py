from src.domain.models.titles import TitleData
from src.infrastructure.db.models import TitleDBModel


class TitleMapper:
    """Mapper class for converting between DB models and domain models."""

    @staticmethod
    def title_db_to_title_data(db_model: TitleDBModel) -> TitleData:
        """Convert a TitleDBModel instance to a TitleData instance."""
        return TitleData.model_validate(db_model, from_attributes=True)
