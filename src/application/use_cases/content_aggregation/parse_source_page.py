from dataclasses import dataclass, field

from src.infrastructure.sources import BaseProvider
from src.domain.interfaces import ITitleRepository


@dataclass
class ParseSourcePageResult:
    upserted: int = 0
    errors: list[Exception] = field(default_factory=list)


class ParseSourcePageUseCase:
    def __init__(
        self,
        title_repository: ITitleRepository,
        source_client: BaseProvider,
    ):
        self._title_repository = title_repository
        self._source_client = source_client

    async def execute(
        self,
        page: int,
        limit: int,
    ) -> ParseSourcePageResult:
        """
        Parse a page of titles from a source and upsert them into the repository.

        Args:
            page (int): The page number to parse.
            limit (int): The number of titles to parse per page.
        """
        result = ParseSourcePageResult()

        try:
            page_content = await self._source_client.get_page(page=page, limit=limit)
            for title in page_content:
                try:
                    async with self._title_repository._session.begin_nested():  # type: ignore
                        title_id = await self._title_repository.upsert_raw_title(
                            raw_title=title,
                        )
                        if title_id:
                            result.upserted += 1
                except Exception as e:
                    result.errors.append(e)
        except Exception as e:
            result.errors.append(e)
            raise e

        return result
