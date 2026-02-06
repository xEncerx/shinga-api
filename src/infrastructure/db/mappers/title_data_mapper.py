from src.domain.models.titles import TitleCover
from src.domain.models.source import Source

from src.infrastructure.db.models import TitleDBModel
from src.domain.models.titles import TitleData

from typing import Any


class TitleDataMapper:
    """Mapper for converting between TitleData (domain) and TitleDBModel (database)."""

    @staticmethod
    def to_domain(data: TitleDBModel | dict[str, Any]) -> TitleData:
        """Convert TitleDBModel to TitleData domain model."""
        return TitleData.model_validate(data, from_attributes=True)

    @staticmethod
    def to_db(
        domain_model: TitleData,
        search_text: str,
        data_quality_score: float,
        primary_source: Source,
        extended_data: dict | None = None,
    ) -> TitleDBModel:
        """
        Convert TitleData domain model to TitleDBModel.

        Note: TitleDBModel requires additional fields that are not part of TitleData:
        - search_text: normalized search text
        - data_quality_score: calculated quality score
        - primary_source: source of the data
        - extended_data: additional metadata
        """
        return TitleDBModel(
            mal_id=domain_model.mal_id,
            search_text=search_text,
            name_ru=domain_model.name_ru,
            name_en=domain_model.name_en,
            alt_names=domain_model.alt_names,
            description_ru=domain_model.description_ru,
            description_en=domain_model.description_en,
            popularity=domain_model.popularity,
            rating=domain_model.rating,
            scored_by=domain_model.scored_by,
            chapters=domain_model.chapters,
            volumes=domain_model.volumes,
            views=domain_model.views,
            favorites=domain_model.favorites,
            genres=domain_model.genres,
            categories=domain_model.categories,
            authors=domain_model.authors,
            cover=domain_model.cover or TitleCover.pending(),
            released_at=domain_model.released_at,
            ended_at=domain_model.ended_at,
            type=domain_model.type,
            status=domain_model.status,
            data_quality_score=data_quality_score,
            primary_source=primary_source,
            extended_data=extended_data or {},
        )
