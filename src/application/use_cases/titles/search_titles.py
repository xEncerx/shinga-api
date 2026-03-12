from dataclasses import dataclass, field

from src.domain.interfaces import ITitleRepository
from src.domain.services import TextNormalizer
from src.domain.models import *


__all__ = ["SearchTitlesUseCase"]


@dataclass(frozen=True)
class TitleSearchItem:
    """Single title with optional user data."""

    title: TitleData
    user_data: UserTitleData | None


@dataclass(frozen=True)
class SearchTitlesResult:
    """Result of title search operation."""

    pagination: Pagination
    content: list[TitleSearchItem] = field(default_factory=list)


class SearchTitlesUseCase:
    """Use case for searching titles with filters, sorting and pagination."""

    def __init__(
        self,
        title_repository: ITitleRepository,
        text_normalizer: TextNormalizer,
    ) -> None:
        self._title_repository = title_repository
        self._text_normalizer = text_normalizer

    async def execute(
        self,
        query: str | None = None,
        type: TitleType | None = None,
        status: TitleStatus | None = None,
        genres: list[str | TitleGenre] | None = None,
        categories: list[str | TitleCategory] | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        min_chapters: int | None = None,
        max_chapters: int | None = None,
        bookmark: TitleBookmark | None = None,
        user_id: int | None = None,
        sort_by: TitleSortBy = TitleSortBy.RATING,
        sort_order: SortingOrder = SortingOrder.DESC,
        page: int = 1,
        page_size: int = 27,
    ) -> SearchTitlesResult:

        normalized_query = None
        if query:
            normalized_query = self._text_normalizer.normalize(query)

        result = await self._title_repository.search_titles(
            query=normalized_query,
            type=type,
            status=status,
            genres=genres,
            categories=categories,
            min_rating=min_rating,
            max_rating=max_rating,
            min_chapters=min_chapters,
            max_chapters=max_chapters,
            bookmark=bookmark,
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

        return SearchTitlesResult(
            pagination=result[0],
            content=[
                TitleSearchItem(
                    title=title_data[0],
                    user_data=title_data[1],
                )
                for title_data in result[1]
            ],
        )
