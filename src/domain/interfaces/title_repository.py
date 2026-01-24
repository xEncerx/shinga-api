from abc import ABC, abstractmethod

from src.domain.models.titles import SourceTitleData, TitleData, TitleCover
from src.domain.models.services.enums import ConsolidationStatus


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
    async def get_master_by_external_id(
        self, **external_id_field
    ) -> tuple[TitleData, int] | None:
        """Find a master title by its source and external ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_master_by_name(
        self,
        normalized_name: str,
        limit: int = 20,
    ) -> list[tuple[TitleData, int]]:
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
