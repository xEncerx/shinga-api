from src.domain.services import TextNormalizer
from src.domain.models.titles import SourceTitleData, TitleData
from src.domain.interfaces import IBaseMatcher


class TitleNameMatcher(IBaseMatcher):
    @property
    def is_definitive(self) -> bool:
        return False

    async def find_candidates(
        self,
        raw_title: SourceTitleData,
    ) -> list[TitleData]:
        td = raw_title.title_data
        normalized_name = TextNormalizer.normalize_multiple(
            [td.name_ru, td.name_en, *td.alt_names],
            deduplicate=True,
            min_word_length=3,
        )
        result = await self._title_repository.get_master_by_name(
            normalized_name,
            limit=20,
        )
        return result
