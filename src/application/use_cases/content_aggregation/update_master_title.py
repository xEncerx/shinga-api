from src.application.use_cases.content_aggregation.merge_master_titles import (
    MergeMasterTitlesUseCase,
)
from src.domain.services import TitleMerger, TitleQualityScorer, TextNormalizer
from src.domain.interfaces import ITitleRepository


class UpdateMasterTitleUseCase:
    def __init__(
        self,
        title_repository: ITitleRepository,
        title_merge_use_case: MergeMasterTitlesUseCase,
        quality_scorer: TitleQualityScorer = TitleQualityScorer(),
        text_normalizer: TextNormalizer = TextNormalizer(),
    ) -> None:
        self._title_repository = title_repository
        self._title_merge_use_case = title_merge_use_case
        self._quality_scorer = quality_scorer
        self._text_normalizer = text_normalizer

    async def execute(self, master_title_id: int) -> None:
        # 1. Retrieve all raw titles linked to the master title
        linked_raw_titles = await self._title_repository.get_raw_titles_by_master_id(
            master_title_id
        )

        if not linked_raw_titles:
            # No raw titles linked, delete the master title to clean up
            await self._title_repository.delete_master_title(master_title_id)
            return

        # 2. Merge the raw titles into a single master title
        merged_title = linked_raw_titles[0]
        for raw_title in linked_raw_titles[1:]:
            merged_title = TitleMerger().merge(merged_title, raw_title)

        # 3. Check for mal_id conflicts
        if merged_title.mal_id:
            existing_master = await self._title_repository.get_master_by_external_id(
                mal_id=merged_title.mal_id
            )
            if existing_master and existing_master.id != master_title_id:
                # Conflict found! It means we have two master titles that belong to the same mal_id.
                await self._title_merge_use_case.execute(
                    target_id=existing_master.id,  # type: ignore
                    source_id=master_title_id,
                )
                # Stop processing current title. The system will update the merged title later.
                return

        # 4. Update the master title in the repository
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
