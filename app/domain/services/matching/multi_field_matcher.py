from sqlmodel import select, or_, func
from typing import Optional, Any

from app.domain.services.matching.base_matcher import *


class MultiFieldMatcher(BaseMatcher):
    """
    Flexible multi-field matcher with confidence-based scoring.

    Strategy:
    1. Search by name (EN/RU/alt) with large limit
    2. Score each candidate by all available fields
    3. Return only candidates above confidence threshold

    Scoring system:
    - Base (name match): 0.85
    - Type match: +0.10 | mismatch: -0.25
    - Year diff ≤1: +0.05 | diff >3: -0.15
    - Status match: +0.05 | mismatch: -0.10
    - Chapters mismatch: -0.10
    - Volumes mismatch: -0.10

    Final confidence: [0.0, 1.0]
    """

    ACCEPTABLE_CHAPTERS_DELTA = 0.10  # 10%
    ACCEPTABLE_VOLUMES_DELTA = 0.10  # 10%
    YEAR_PERFECT_MATCH = 1
    YEAR_BAD_DIFF = 3

    def get_strategy_name(self):
        return MatchingStrategy.MULTI_FIELD

    def get_min_confidence(self):
        return 0.75

    async def find_matches(
        self,
        title_data: TitleData,
        limit: int = 5,
    ) -> list[TitleMatchCandidate]:
        candidates = []
        seen_master_ids = set()

        # Collect all possible names for search
        search_names = self._collect_search_names(title_data)
        if not search_names:
            logger.warning("MultiFieldMatcher: No valid search names provided")
            return []

        # Extract year safely
        year_from = self._extract_year(title_data.date)

        # Step 1: Search by names only with large limit
        possible_titles = await self._search_by_names(search_names, limit)

        logger.debug(
            f"MultiFieldMatcher: Found {len(possible_titles)} titles by name search"
        )

        # Step 2: Score each candidate by all available fields
        for title in possible_titles:
            if title.id in seen_master_ids:
                continue

            confidence, details = self._calculate_confidence(
                title=title,
                title_data=title_data,
                year_from=year_from,
            )

            if confidence >= self.get_min_confidence():
                candidate = self._create_candidate(
                    master_title_id=title.id,  # type: ignore
                    confidence=min(confidence, 1.0),  # Cap at 1.0
                    details=details,
                )
                candidates.append(candidate)
                seen_master_ids.add(title.id)

                if len(candidates) >= limit:
                    break

        # Sort by confidence descending
        candidates.sort(key=lambda x: x.confidence, reverse=True)

        logger.debug(
            f"MultiFieldMatcher: Returning {len(candidates)} candidates "
            f"(threshold: {self.get_min_confidence()})"
        )
        return candidates[:limit]

    def _collect_search_names(self, title_data: TitleData) -> list[str]:
        """Collect all valid search names from title data."""
        names = []

        # Add EN name
        if title_data.name_en and len(title_data.name_en.strip()) >= 2:
            names.append(title_data.name_en.strip())

        # Add RU name
        if title_data.name_ru and len(title_data.name_ru.strip()) >= 2:
            names.append(title_data.name_ru.strip())

        # Add alternative names
        if title_data.alt_names:
            for alt_name in title_data.alt_names:
                if alt_name and len(alt_name.strip()) >= 2:
                    cleaned_name = alt_name.strip()
                    if cleaned_name not in names:  # Avoid duplicates
                        names.append(cleaned_name)

        return names

    def _extract_year(self, date_info: Optional[Any]) -> Optional[int]:
        """Safely extract year from date field."""
        if not date_info:
            return None

        try:
            # Handle dict-like date objects
            from_date = None
            if hasattr(date_info, "from_"):
                from_date = date_info.from_
            elif isinstance(date_info, dict) and "from_" in date_info:
                from_date = date_info["from_"]

            if not from_date:
                return None

            # Extract year from string
            if isinstance(from_date, str):
                year_str = from_date[:4]
                if year_str.isdigit() and len(year_str) == 4:
                    year = int(year_str)
                    # Validate reasonable year range
                    if 1900 <= year <= 2100:
                        return year

            # Handle datetime objects
            elif hasattr(from_date, "year"):
                return from_date.year

        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"MultiFieldMatcher: Failed to extract year: {e}")

        return None

    async def _search_by_names(
        self, search_names: list[str], limit: int
    ) -> list[Title]:
        """Search titles by names only, return generous results."""
        query = select(Title)

        # Build OR conditions for all names
        name_filters = []
        for name in search_names:
            name_lower = name.lower()
            name_filters.append(func.lower(Title.name_en) == name_lower)
            name_filters.append(func.lower(Title.name_ru) == name_lower)

        if not name_filters:
            return []

        # Apply name filter with generous limit
        query = query.where(or_(*name_filters))
        query = query.limit(max(limit * 5, 50))

        result = await self.session.exec(query)
        return list(result.all())

    def _calculate_confidence(
        self,
        title: Title,
        title_data: TitleData,
        year_from: Optional[int],
    ) -> tuple[float, dict]:
        """
        Calculate confidence score based on all available fields.

        Returns:
            (confidence_score, details_dict)
        """
        confidence = 0.85  # Base for name match
        details: dict[str, Any] = {
            "matched_name": title.name_en or title.name_ru or "N/A",
        }

        # Type matching (critical field)
        type_match = self._check_type_match(title.type_, title_data.type_)
        details["type"] = title.type_
        details["type_match"] = type_match

        if type_match is True:
            confidence += 0.10
        elif type_match is False:
            confidence -= 0.25

        # Year matching
        year_diff = self._calculate_year_diff(title, year_from)
        details["year_diff"] = year_diff

        if year_diff is not None:
            if year_diff <= self.YEAR_PERFECT_MATCH:
                confidence += 0.05
            elif year_diff > self.YEAR_BAD_DIFF:
                confidence -= 0.15
            # Medium difference (2-3 years): neutral

        # Status matching
        status_match = self._check_status_match(title.status, title_data.status)
        details["status"] = title.status
        details["status_match"] = status_match

        if status_match is True:
            confidence += 0.05
        elif status_match is False:
            confidence -= 0.10

        # Chapters matching (non-critical)
        chapters_ok = self._check_chapters_match(title.chapters, title_data.chapters)
        details["chapters_match"] = chapters_ok
        details["title_chapters"] = title.chapters
        details["input_chapters"] = title_data.chapters

        if not chapters_ok:
            confidence -= 0.10

        # Volumes matching (non-critical)
        volumes_ok = self._check_volumes_match(title.volumes, title_data.volumes)
        details["volumes_match"] = volumes_ok
        details["title_volumes"] = title.volumes
        details["input_volumes"] = title_data.volumes

        if not volumes_ok:
            confidence -= 0.10

        return confidence, details

    def _check_type_match(
        self,
        title_type: Optional[str],
        input_type: Optional[str],
    ) -> Optional[bool]:
        """Check if types match (case-insensitive)."""
        if not title_type or not input_type:
            return None
        return title_type.lower() == input_type.lower()

    def _calculate_year_diff(
        self,
        title: Title,
        input_year: Optional[int],
    ) -> Optional[int]:
        """Calculate year difference, return None if can't compare."""
        if not input_year:
            return None

        title_year = self._extract_year(title.date)
        if not title_year:
            return None

        return abs(title_year - input_year)

    def _check_status_match(
        self,
        title_status: Optional[str],
        input_status: Optional[str],
    ) -> Optional[bool]:
        """Check if statuses match (case-insensitive)."""
        if not title_status or not input_status:
            return None
        return title_status.lower() == input_status.lower()

    def _check_chapters_match(
        self,
        title_chapters: Optional[int],
        input_chapters: Optional[int],
    ) -> bool:
        """
        Check if chapter counts are acceptable.
        Returns True if match or if data is missing (benefit of doubt).
        """
        if not title_chapters or not input_chapters:
            return True  # Missing data - no penalty

        delta = max(int(title_chapters * self.ACCEPTABLE_CHAPTERS_DELTA), 1)
        return abs(title_chapters - input_chapters) <= delta

    def _check_volumes_match(
        self,
        title_volumes: Optional[int],
        input_volumes: Optional[int],
    ) -> bool:
        """
        Check if volume counts are acceptable.
        Returns True if match or if data is missing (benefit of doubt).
        """
        if not title_volumes or not input_volumes:
            return True  # Missing data - no penalty

        delta = max(int(title_volumes * self.ACCEPTABLE_VOLUMES_DELTA), 1)
        return abs(title_volumes - input_volumes) <= delta
