from typing import TypeVar
from thefuzz import fuzz

from src.domain.models.titles import TitleData, TitleGenre, TitleCategory


TEnum = TypeVar("TEnum", TitleGenre, TitleCategory)


class TitleMerger:
    """Service for merging title data from multiple sources."""

    _SIMILARITY_THRESHOLD = 85

    def merge(self, existing: TitleData, new: TitleData) -> TitleData:
        """
        Merge two title data objects, prioritizing existing data where appropriate.

        Args:
            existing: The existing title data (usually from master table)
            new: New title data to merge into existing

        Returns:
            TitleData: Merged title data
        """
        return TitleData(
            mal_id=existing.mal_id or new.mal_id,
            name_ru=existing.name_ru or new.name_ru,
            name_en=existing.name_en or new.name_en,
            description_ru=existing.description_ru or new.description_ru,
            description_en=existing.description_en or new.description_en,
            type=existing.type,
            status=new.status,
            popularity=max(existing.popularity, new.popularity),
            chapters=max(existing.chapters, new.chapters),
            views=max(existing.views, new.views),
            volumes=max(existing.volumes, new.volumes),
            favorites=max(existing.favorites, new.favorites),
            rating=self._calculate_weighted_rating(
                existing.rating,
                existing.scored_by,
                new.rating,
                new.scored_by,
            ),
            scored_by=existing.scored_by + new.scored_by,
            released_at=existing.released_at or new.released_at,
            ended_at=existing.ended_at or new.ended_at,
            genres=self._merge_unique_enums(existing.genres, new.genres),
            categories=self._merge_unique_enums(existing.categories, new.categories),
            authors=self._merge_strings_with_fuzzy(existing.authors, new.authors),
            alt_names=self._merge_strings_with_fuzzy(existing.alt_names, new.alt_names),
            cover=existing.cover,
        )

    def _calculate_weighted_rating(
        self,
        rating1: float,
        scored_by1: int,
        rating2: float,
        scored_by2: int,
    ) -> float:
        """Calculate weighted average rating."""
        total_scores = scored_by1 + scored_by2

        if total_scores == 0:
            return 0.0

        weighted_rating = (rating1 * scored_by1 + rating2 * scored_by2) / total_scores
        return round(weighted_rating, 2)

    def _merge_unique_enums(
        self,
        existing_items: list[TEnum],
        new_items: list[TEnum],
    ) -> list[TEnum]:
        """Merge two lists of enums, removing duplicates."""
        unique_items = set(existing_items) | set(new_items)
        return list(unique_items)

    def _merge_strings_with_fuzzy(
        self,
        existing_strings: list[str],
        new_strings: list[str],
    ) -> list[str]:
        """Merge two lists of strings, removing similar duplicates using fuzzy matching."""
        result = existing_strings.copy()

        for new_string in new_strings:
            is_duplicate = False

            for existing_string in result:
                similarity = fuzz.token_sort_ratio(
                    new_string.lower().strip(), existing_string.lower().strip()
                )

                if similarity >= self._SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    break

            if not is_duplicate:
                result.append(new_string)

        return result
