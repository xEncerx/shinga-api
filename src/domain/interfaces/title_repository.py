from abc import ABC, abstractmethod

from src.domain.models import *


class ITitleRepository(ABC):
    @abstractmethod
    async def upsert_raw_title(
        self,
        raw_title: SourceTitleData,
    ) -> int | None:
        """Insert or update a raw title record in the database."""
        raise NotImplementedError

    @abstractmethod
    async def get_raw_title(self, raw_title_id: int) -> SourceTitleData | None:
        """Retrieve a raw title record by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_unmapped_raw_titles(self, limit: int) -> list[int]:
        """Retrieve a list of raw titles with pending consolidation status."""
        raise NotImplementedError

    @abstractmethod
    async def update_consolidation_status(
        self,
        raw_title_id: int,
        status: ConsolidationStatus,
        detail: str | None = None,
    ) -> None:
        """Update the consolidation status of a raw title."""
        raise NotImplementedError

    @abstractmethod
    async def link_raw_to_master(self, raw_title_id: int, master_title_id: int) -> None:
        """Link a raw title to a master title."""
        raise NotImplementedError

    @abstractmethod
    async def add_master_title(
        self,
        title_data: SourceTitleData,
        search_text: str,
        data_quality_score: float,
    ) -> int:
        """
        Add a new master title record to the database.

        Args:
            title_data (SourceTitleData): The source title data to be added as a master title.
            search_text (str): The normalized search text for the title.
            data_quality_score (float): The quality score of the title data.

        Returns:
            int: The ID of the newly created master title.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_master_title(
        self,
        master_title_id: int,
        title_data: TitleData,
        search_text: str,
        data_quality_score: float,
    ) -> None:
        """Update an existing master title record in the database."""
        raise NotImplementedError

    @abstractmethod
    async def get_master_title(self, master_title_id: int) -> TitleData | None:
        """Retrieve a master title record by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_master_by_external_id(self, **external_id_field) -> TitleData | None:
        """Find a master title by its source and external ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_master_by_name(
        self,
        normalized_name: str,
        limit: int = 20,
    ) -> list[TitleData]:
        """Find master titles by name. Uses normalized name and vector search"""
        raise NotImplementedError

    @abstractmethod
    async def get_master_title_for_update(
        self,
        hours: int = 128,
        limit: int = 100,
        last_id: int = 0,
    ) -> list[int]:
        """Retrieve master titles for update processing."""
        raise NotImplementedError

    @abstractmethod
    async def get_raw_titles_by_master_id(
        self, master_title_id: int
    ) -> list[TitleData]:
        """Retrieve raw titles linked to a specific master title ID."""
        raise NotImplementedError

    @abstractmethod
    async def update_master_title_cover(
        self,
        master_title_id: int,
        cover: TitleCover,
    ) -> None:
        """Update the cover image information for a master title."""
        raise NotImplementedError

    @abstractmethod
    async def search_titles(
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
        order: SortingOrder = SortingOrder.DESC,
        page: int = 1,
        page_size: int = 27,
    ) -> tuple[Pagination, list[tuple[TitleData, UserTitleData | None]]]:
        """
        Search titles with filters, sorting and pagination.

        Args:
            query: Normalized search query for fulltext search
            type: Filter by title type
            status: Filter by title status
            genres: Filter by genres (any match)
            categories: Filter by categories (any match)
            min_rating: Filter by minimum rating
            max_rating: Filter by maximum rating
            min_chapters: Filter by minimum number of chapters
            max_chapters: Filter by maximum number of chapters
            bookmark: Filter by user's bookmark status
            user_id: User ID for retrieving user-specific data and bookmark filter
            sort_by: Field to sort by
            order: Sorting order (asc/desc)
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            A tuple containing pagination info and a list of title data with optional user title data.
        """
        raise NotImplementedError
