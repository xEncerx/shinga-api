from src.domain.services import TitleMerger, TitleQualityScorer, TextNormalizer
from src.domain.interfaces import ITitleRepository


class UpdateMasterTitleUseCase:
    def __init__(
        self,
        title_repository: ITitleRepository,
        quality_scorer: TitleQualityScorer = TitleQualityScorer(),
        text_normalizer: TextNormalizer = TextNormalizer(),
    ) -> None:
        self._title_repository = title_repository
        self._quality_scorer = quality_scorer
        self._text_normalizer = text_normalizer

    async def execute(self, master_title_id: int) -> None:
        # 1. Retrieve all raw titles linked to the master title
        linked_raw_titles = await self._title_repository.get_raw_titles_by_master_id(
            master_title_id
        )
        # 2. Merge the raw titles into a single master title
        merged_title = linked_raw_titles[0]
        for raw_title in linked_raw_titles[1:]:
            merged_title = TitleMerger().merge(merged_title, raw_title)

        # 3. Update the master title in the repository
        await self._title_repository.update_master_title(
            master_title_id=master_title_id,
            title_data=merged_title,
            search_text=self._text_normalizer.normalize_multiple(
                [
                    merged_title.name_ru,
                    merged_title.name_en,
                    *merged_title.alt_names,
                ],
            ),
            data_quality_score=self._quality_scorer.score(merged_title),
        )
