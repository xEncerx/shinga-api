from datetime import datetime
from thefuzz import fuzz

from src.domain.models.titles import TitleData, TitleCover
from src.domain.services import TextNormalizer


class TitleSimilarityScorer:
    """
    Service for evaluating similarity between two titles.

    Used in consolidation process to determine if two titles are likely the same.
    Only scores fields that exist in both titles.
    If the score is >= 85, it is highly likely that these are the same title.

    Scoring system (max 100 points):
    - Names (45 points): name_ru, name_en, alt_names cross-matching
    - Type and Status (15 points): type is blocking field
    - Release info (15 points): released_at, ended_at with tolerance
    - Numeric data (8 points): chapters, volumes with tolerance
    - Lists (10 points): genres, categories, authors overlap
    - Descriptions (7 points): description_ru, description_en
    """

    _SCORE_NAMES = 45.0
    _SCORE_TYPE = 10.0
    _SCORE_STATUS = 5.0
    _SCORE_DATES = 15.0
    _SCORE_NUMERIC = 8.0
    _SCORE_LISTS = 10.0
    _SCORE_DESCRIPTIONS = 7.0

    _DATE_TOLERANCE_DAYS = 365
    _NUMERIC_TOLERANCE_PERCENT = 0.15

    def score(self, title_a: TitleData, title_b: TitleData) -> float:
        if title_a.type != title_b.type:
            return 0.0

        # Names are blocking field - cannot compare without names
        names_a = self._collect_all_names(title_a)
        names_b = self._collect_all_names(title_b)
        if not names_a or not names_b:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        name_score, name_weight = self._score_names(title_a, title_b)
        total_score += name_score
        total_weight += name_weight

        type_score, type_weight = self._score_type_and_status(title_a, title_b)
        total_score += type_score
        total_weight += type_weight

        date_score, date_weight = self._score_dates(title_a, title_b)
        total_score += date_score
        total_weight += date_weight

        numeric_score, numeric_weight = self._score_numeric_fields(title_a, title_b)
        total_score += numeric_score
        total_weight += numeric_weight

        list_score, list_weight = self._score_lists(title_a, title_b)
        total_score += list_score
        total_weight += list_weight

        desc_score, desc_weight = self._score_descriptions(title_a, title_b)
        total_score += desc_score
        total_weight += desc_weight

        if total_weight == 0:
            return 0.0

        normalized_score = (total_score / total_weight) * 100.0
        return round(min(normalized_score, 100.0), 2)

    def _score_names(
        self, title_a: TitleData, title_b: TitleData
    ) -> tuple[float, float]:
        all_names_a = self._collect_all_names(title_a)
        all_names_b = self._collect_all_names(title_b)

        if not all_names_a or not all_names_b:
            return (0.0, 0.0)

        max_similarity = 0.0
        for _, normalized_a in all_names_a:
            for _, normalized_b in all_names_b:
                similarity = fuzz.token_sort_ratio(normalized_a, normalized_b) / 100.0
                max_similarity = max(max_similarity, similarity)

        return (max_similarity * self._SCORE_NAMES, self._SCORE_NAMES)

    def _collect_all_names(self, title: TitleData) -> list[tuple[str, str]]:
        names = []
        seen = set()

        candidates = [title.name_ru, title.name_en]
        if title.alt_names:
            candidates.extend(title.alt_names)

        for name in candidates:
            if name and name.strip():
                normalized = TextNormalizer.normalize(name)
                if normalized and normalized not in seen:
                    names.append((name.strip(), normalized))
                    seen.add(normalized)

        return names

    def _score_descriptions(
        self, title_a: TitleData, title_b: TitleData
    ) -> tuple[float, float]:
        descriptions_a = self._collect_descriptions(title_a)
        descriptions_b = self._collect_descriptions(title_b)

        if not descriptions_a or not descriptions_b:
            return (0.0, 0.0)

        max_similarity = 0.0
        for _, normalized_a in descriptions_a:
            for _, normalized_b in descriptions_b:
                similarity = fuzz.partial_ratio(normalized_a, normalized_b) / 100.0
                max_similarity = max(max_similarity, similarity)

        return (max_similarity * self._SCORE_DESCRIPTIONS, self._SCORE_DESCRIPTIONS)

    def _collect_descriptions(self, title: TitleData) -> list[tuple[str, str]]:
        descriptions = []

        for desc in [title.description_ru, title.description_en]:
            if desc and desc.strip():
                normalized = TextNormalizer.normalize(desc)
                if normalized:
                    descriptions.append((desc.strip(), normalized))

        return descriptions

    def _score_type_and_status(
        self, title_a: TitleData, title_b: TitleData
    ) -> tuple[float, float]:
        score = self._SCORE_TYPE
        weight = self._SCORE_TYPE

        if title_a.status == title_b.status:
            score += self._SCORE_STATUS
        weight += self._SCORE_STATUS

        return (score, weight)

    def _score_dates(
        self, title_a: TitleData, title_b: TitleData
    ) -> tuple[float, float]:
        score = 0.0
        weight = 0.0

        if title_a.released_at is not None and title_b.released_at is not None:
            released_similarity = self._date_similarity(
                title_a.released_at, title_b.released_at
            )
            score += released_similarity * (self._SCORE_DATES / 2)
            weight += self._SCORE_DATES / 2

        if title_a.ended_at is not None and title_b.ended_at is not None:
            ended_similarity = self._date_similarity(title_a.ended_at, title_b.ended_at)
            score += ended_similarity * (self._SCORE_DATES / 2)
            weight += self._SCORE_DATES / 2

        return (score, weight)

    def _date_similarity(self, date_a: datetime, date_b: datetime) -> float:
        # Normalize to naive datetime for comparison
        if date_a.tzinfo is not None:
            date_a = date_a.replace(tzinfo=None)
        if date_b.tzinfo is not None:
            date_b = date_b.replace(tzinfo=None)

        days_diff = abs((date_a - date_b).days)

        if days_diff == 0:
            return 1.0
        elif days_diff <= self._DATE_TOLERANCE_DAYS:
            return 1.0 - (days_diff / self._DATE_TOLERANCE_DAYS)
        else:
            return 0.0

    def _score_numeric_fields(
        self, title_a: TitleData, title_b: TitleData
    ) -> tuple[float, float]:
        score = 0.0
        weight = 0.0

        if title_a.chapters > 0 and title_b.chapters > 0:
            chapters_similarity = self._numeric_similarity(
                title_a.chapters, title_b.chapters
            )
            score += chapters_similarity * (self._SCORE_NUMERIC / 2)
            weight += self._SCORE_NUMERIC / 2

        if title_a.volumes > 0 and title_b.volumes > 0:
            volumes_similarity = self._numeric_similarity(
                title_a.volumes, title_b.volumes
            )
            score += volumes_similarity * (self._SCORE_NUMERIC / 2)
            weight += self._SCORE_NUMERIC / 2

        return (score, weight)

    def _numeric_similarity(self, value_a: int, value_b: int) -> float:
        max_val = max(value_a, value_b)
        min_val = min(value_a, value_b)

        if max_val == 0:
            return 1.0

        diff_percent = (max_val - min_val) / max_val

        if diff_percent <= self._NUMERIC_TOLERANCE_PERCENT:
            return 1.0
        elif diff_percent <= self._NUMERIC_TOLERANCE_PERCENT * 2:
            return 1.0 - (
                (diff_percent - self._NUMERIC_TOLERANCE_PERCENT)
                / self._NUMERIC_TOLERANCE_PERCENT
            )
        else:
            return 0.0

    def _score_lists(
        self, title_a: TitleData, title_b: TitleData
    ) -> tuple[float, float]:
        score = 0.0
        weight = 0.0

        if title_a.genres and title_b.genres:
            genres_similarity = self._overlap_coefficient(
                [g.value for g in title_a.genres], [g.value for g in title_b.genres]
            )
            score += genres_similarity * (self._SCORE_LISTS / 3)
            weight += self._SCORE_LISTS / 3

        if title_a.categories and title_b.categories:
            categories_similarity = self._overlap_coefficient(
                [c.value for c in title_a.categories],
                [c.value for c in title_b.categories],
            )
            score += categories_similarity * (self._SCORE_LISTS / 3)
            weight += self._SCORE_LISTS / 3

        if title_a.authors and title_b.authors:
            authors_similarity = self._overlap_coefficient(
                title_a.authors, title_b.authors
            )
            score += authors_similarity * (self._SCORE_LISTS / 3)
            weight += self._SCORE_LISTS / 3

        return (score, weight)

    def _overlap_coefficient(self, list_a: list, list_b: list) -> float:
        if not list_a or not list_b:
            return 0.0

        set_a = set(list_a)
        set_b = set(list_b)

        intersection = len(set_a & set_b)
        min_size = min(len(set_a), len(set_b))

        return intersection / min_size if min_size > 0 else 0.0


class TitleQualityScorer:
    """
    Service for calculating data quality score for title based on all fields.

    Scoring system (max 100 points):
    - Critical fields (50 points): name_ru, name_en, rating, chapters, cover_url
    - Important fields (30 points): descriptions, genres, categories, authors
    - Additional fields (20 points): alt_names, dates, volumes, engagement metrics
    """

    _SCORE_NAME_RU = 12.0
    _SCORE_NAME_EN = 12.0
    _SCORE_RATING_BASE = 10.0
    _SCORE_RATING_WITH_SCORED_BY = 2.0
    _SCORE_CHAPTERS = 7.0
    _SCORE_COVER_URL = 7.0

    _SCORE_DESCRIPTION_BASE = 5.0
    _SCORE_DESCRIPTION_LENGTH_BONUS = 3.0
    _DESCRIPTION_MIN_LENGTH = 50
    _DESCRIPTION_OPTIMAL_LENGTH = 300

    _SCORE_GENRES_MAX = 5.0
    _SCORE_CATEGORIES_MAX = 5.0
    _SCORE_AUTHORS = 4.0

    _SCORE_ALT_NAMES = 3.0
    _SCORE_RELEASED_AT = 3.0
    _SCORE_ENDED_AT = 3.0
    _SCORE_VOLUMES = 2.0
    _SCORE_ENGAGEMENT_MAX = 6.0
    _SCORE_POPULARITY = 3.0

    _NAME_MIN_LENGTH = 3
    _NAME_GOOD_LENGTH = 10

    def score(self, title: TitleData) -> float:
        total_score = 0.0

        total_score += self._score_name_ru(title.name_ru)
        total_score += self._score_name_en(title.name_en)
        total_score += self._score_rating(title.rating, title.scored_by)
        total_score += self._score_chapters(title.chapters)
        total_score += self._score_cover(title.cover)

        total_score += self._score_description(title.description_ru)
        total_score += self._score_description(title.description_en)
        total_score += self._score_genres(title.genres)
        total_score += self._score_categories(title.categories)
        total_score += self._score_authors(title.authors)

        total_score += self._score_alt_names(title.alt_names)
        total_score += self._score_released_at(title.released_at)
        total_score += self._score_ended_at(title.ended_at)
        total_score += self._score_volumes(title.volumes)
        total_score += self._score_engagement_metrics(
            title.views, title.favorites, title.popularity
        )

        return round(min(total_score, 100.0), 2)

    def _score_name_ru(self, name_ru: str | None) -> float:
        if not name_ru or not name_ru.strip():
            return 0.0

        length = len(name_ru.strip())
        if length < self._NAME_MIN_LENGTH:
            return self._SCORE_NAME_RU * 0.5
        elif length < self._NAME_GOOD_LENGTH:
            return self._SCORE_NAME_RU * 0.8
        return self._SCORE_NAME_RU

    def _score_name_en(self, name_en: str | None) -> float:
        if not name_en or not name_en.strip():
            return 0.0

        length = len(name_en.strip())
        if length < self._NAME_MIN_LENGTH:
            return self._SCORE_NAME_EN * 0.5
        elif length < self._NAME_GOOD_LENGTH:
            return self._SCORE_NAME_EN * 0.8
        return self._SCORE_NAME_EN

    def _score_rating(self, rating: float, scored_by: int) -> float:
        if rating <= 0:
            return 0.0

        score = self._SCORE_RATING_BASE
        if scored_by > 0:
            score += self._SCORE_RATING_WITH_SCORED_BY

        return score

    def _score_chapters(self, chapters: int) -> float:
        return self._SCORE_CHAPTERS if chapters > 0 else 0.0

    def _score_cover(self, cover: TitleCover | None) -> float:
        return (
            self._SCORE_COVER_URL
            if cover and any([cover.thumbnail, cover.original])
            else 0.0
        )

    def _score_description(self, description: str | None) -> float:
        if not description or not description.strip():
            return 0.0

        desc_len = len(description.strip())

        if desc_len < self._DESCRIPTION_MIN_LENGTH:
            return self._SCORE_DESCRIPTION_BASE * (
                desc_len / self._DESCRIPTION_MIN_LENGTH
            )

        score = self._SCORE_DESCRIPTION_BASE

        if desc_len >= self._DESCRIPTION_OPTIMAL_LENGTH:
            score += self._SCORE_DESCRIPTION_LENGTH_BONUS
        else:
            length_ratio = (desc_len - self._DESCRIPTION_MIN_LENGTH) / (
                self._DESCRIPTION_OPTIMAL_LENGTH - self._DESCRIPTION_MIN_LENGTH
            )
            score += self._SCORE_DESCRIPTION_LENGTH_BONUS * length_ratio

        return score

    def _score_genres(self, genres: list) -> float:
        if not genres:
            return 0.0

        genre_count = len(genres)
        if genre_count >= 3:
            return self._SCORE_GENRES_MAX
        elif genre_count == 2:
            return self._SCORE_GENRES_MAX * 0.7
        return self._SCORE_GENRES_MAX * 0.4

    def _score_categories(self, categories: list) -> float:
        if not categories:
            return 0.0

        category_count = len(categories)
        if category_count >= 3:
            return self._SCORE_CATEGORIES_MAX
        elif category_count == 2:
            return self._SCORE_CATEGORIES_MAX * 0.7
        return self._SCORE_CATEGORIES_MAX * 0.4

    def _score_authors(self, authors: list[str]) -> float:
        return self._SCORE_AUTHORS if authors and len(authors) > 0 else 0.0

    def _score_alt_names(self, alt_names: list[str]) -> float:
        return self._SCORE_ALT_NAMES if alt_names and len(alt_names) > 0 else 0.0

    def _score_released_at(self, released_at) -> float:
        return self._SCORE_RELEASED_AT if released_at is not None else 0.0

    def _score_ended_at(self, ended_at) -> float:
        return self._SCORE_ENDED_AT if ended_at is not None else 0.0

    def _score_volumes(self, volumes: int) -> float:
        return self._SCORE_VOLUMES if volumes > 0 else 0.0

    def _score_engagement_metrics(
        self, views: int, favorites: int, popularity: int
    ) -> float:
        score = 0.0

        if popularity > 0:
            score += self._SCORE_POPULARITY

        has_engagement = score > 0
        if views > 0:
            score += 2.0 if not has_engagement else 1.0
            has_engagement = True
        if favorites > 0:
            score += 2.0 if not has_engagement else 1.0

        return min(score, self._SCORE_ENGAGEMENT_MAX + self._SCORE_POPULARITY)
