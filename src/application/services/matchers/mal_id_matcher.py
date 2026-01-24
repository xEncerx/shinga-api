from src.domain.models.titles import SourceTitleData, TitleData
from src.domain.interfaces import IBaseMatcher


class MalIdMatcher(IBaseMatcher):
    @property
    def is_definitive(self) -> bool:
        return True

    async def find_candidates(
        self, raw_title: SourceTitleData
    ) -> list[tuple[TitleData, int]]:
        mal_id = raw_title.title_data.mal_id
        if not mal_id:
            return []

        master = await self._title_repository.get_master_by_external_id(mal_id=mal_id)
        return [master] if master else []
