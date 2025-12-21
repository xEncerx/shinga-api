from datetime import datetime

from app.tasks.download_media import download_cover_task
from app.infrastructure.db.models.title import Title
from app.domain.models import TitleData
from app.core import logger, settings
from app.infrastructure.db.models.title.relations import (
    TitleCover,
    TitleDescription,
    TitleReleaseTime,
)


class DataMerger:
    """
    Merging data from different sources into a master title.

    Implements data combination logic:
    - Names: merge, avoid duplicates
    - Descriptions: take from different languages
    - Ratings: weighted average of non-zero values
    - Numeric data: maximum (except rating)
    - Covers: source priority
    """

    def merge_sources(
        self,
        existing_title: Title,
        new_title_data: TitleData,
    ) -> Title:
        """
        Merge new source data with existing master title.

        Args:
            existing_title: Existing master title
            new_title_data: New data from source

        Returns:
            Updated Title
        """
        # === Name ===
        merged_name_en = existing_title.name_en or new_title_data.name_en
        merged_name_ru = existing_title.name_ru or new_title_data.name_ru

        # === Alternative names ===
        existing_alt_names = set(existing_title.alt_names or [])
        new_alt_names = set(new_title_data.alt_names or [])

        merged_alt_names = list(existing_alt_names | new_alt_names)

        # === Description ===
        merged_desc_en = existing_title.description.en or new_title_data.description.en
        merged_desc_ru = existing_title.description.ru or new_title_data.description.ru

        merged_description = TitleDescription(en=merged_desc_en, ru=merged_desc_ru)

        # === Rating and scores ===
        existing_rating = existing_title.rating or 0.0
        new_rating = new_title_data.rating or 0.0
        existing_scored_by = existing_title.scored_by or 0
        new_scored_by = new_title_data.scored_by or 0

        # Weighted average
        if existing_scored_by > 0 and new_scored_by > 0:
            merged_rating = (
                existing_rating * existing_scored_by + new_rating * new_scored_by
            ) / (existing_scored_by + new_scored_by)
            merged_scored_by = existing_scored_by + new_scored_by
        elif new_scored_by > 0:
            merged_rating = new_rating
            merged_scored_by = new_scored_by
        else:
            merged_rating = existing_rating
            merged_scored_by = existing_scored_by

        # === Numeric fields (maximum) ===
        merged_chapters = max(
            existing_title.chapters or 0,
            new_title_data.chapters or 0,
        )
        merged_volumes = max(
            existing_title.volumes or 0,
            new_title_data.volumes or 0,
        )
        merged_views = max(
            existing_title.views or 0,
            new_title_data.views or 0,
        )
        merged_popularity = min(  # Lower popularity = higher rank
            existing_title.popularity or 999999,
            new_title_data.popularity or 999999,
        )
        merged_favorites = max(
            existing_title.favorites or 0,
            new_title_data.favorites or 0,
        )

        # === Authors ===
        existing_authors = set(existing_title.authors or [])
        new_authors = set(new_title_data.authors or [])
        merged_authors = list(existing_authors | new_authors)

        # === Genres ===
        existing_genres = set(existing_title.genres or [])
        new_genres = set(new_title_data.genres or [])
        merged_genres = list(existing_genres | new_genres)

        # === Status and type ===
        merged_type = new_title_data.type_ or existing_title.type_
        merged_status = new_title_data.status or existing_title.status

        # === Release date ===
        merged_date = existing_title.date
        if new_title_data.date:
            if not merged_date or not merged_date.from_:
                merged_date = TitleReleaseTime(
                    from_=new_title_data.date.from_ or existing_title.date.from_,
                    to=new_title_data.date.to or existing_title.date.to,
                )

        # === Cover ===
        merged_cover = existing_title.cover
        if (
            not merged_cover.url or merged_cover.url.startswith("http")
        ) or merged_cover.url == settings.COVER_404_PATH:
            merged_cover = self.download_covers(
                title_id=existing_title.id,  # type: ignore
                cover_url=new_title_data.cover.url,  # type: ignore
                source_provider=new_title_data.source_provider,
            )

        # === Update existing title ===
        existing_title.name_en = merged_name_en
        existing_title.name_ru = merged_name_ru
        existing_title.alt_names = merged_alt_names
        existing_title.description = merged_description
        existing_title.rating = round(merged_rating, 2)
        existing_title.scored_by = merged_scored_by
        existing_title.chapters = merged_chapters
        existing_title.volumes = merged_volumes
        existing_title.views = merged_views
        existing_title.popularity = (
            merged_popularity if merged_popularity != 999999 else 0
        )
        existing_title.favorites = merged_favorites
        existing_title.authors = merged_authors
        existing_title.genres = merged_genres
        existing_title.type_ = merged_type
        existing_title.status = merged_status
        existing_title.date = merged_date
        existing_title.cover = merged_cover
        existing_title.updated_at = datetime.now()

        logger.debug(
            f"Merged title data: {existing_title.name_en or existing_title.name_ru} (rating={merged_rating:.2f})"
        )

        return existing_title

    def download_covers(
        self,
        title_id: int | None,
        cover_url: str,
        source_provider: str,
    ) -> TitleCover:
        """
        Start task for downloading covers. Return placeholder for now.

        Args:
            title_id: ID of title in master titles
            cover_url: Cover URL
            source_provider: Source provider
        """
        download_cover_task.apply_async(
            kwargs={
                "title_id": title_id,
                "cover_url": cover_url,
                "source_provider": source_provider,
            },
            priority=5,
        )

        return TitleCover.pending_placeholder()

    @staticmethod
    def calculate_data_quality_score(title: Title) -> float:
        """
        Calculate data quality score for title.

        Based on data completeness:
        - Both names: +0.2
        - Description: +0.15
        - Authors: +0.1
        - Genres: +0.1
        - Cover: +0.15
        - Rating with scores: +0.15
        - Type and status: +0.15

        Args:
            title: Title to evaluate

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0

        # Names (maximum 0.2)
        if title.name_en and title.name_ru:
            score += 0.2
        elif title.name_en or title.name_ru:
            score += 0.1

        # Description (0.15)
        if title.description and (title.description.en or title.description.ru):
            score += 0.15

        # Authors (0.1)
        if title.authors and len(title.authors) > 0:
            score += 0.1

        # Genres (0.1)
        if title.genres and len(title.genres) > 0:
            score += 0.1

        # Cover (0.15)
        if title.cover and title.cover.url:
            score += 0.15

        # Rating with scores (0.15)
        if title.rating > 0 and title.scored_by > 10:
            score += 0.15
        elif title.scored_by > 0:
            score += 0.08

        # Status and type (0.15)
        if title.type_ and title.status:
            score += 0.15

        return min(1.0, score)  # No more than 1.0
