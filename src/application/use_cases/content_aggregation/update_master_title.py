from src.domain.services import TitleMerger, TitleQualityScorer, TextNormalizer
from src.domain.interfaces import ITitleRepository
from src.domain.models.services import ConsolidationStatus
from src.domain.models import TitleData


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
                # Conflict found!
                linked_raw_titles = await self._detach_problematic_titles(
                    linked_raw_titles, merged_title.mal_id
                )
                
                # If no titles left after detaching, delete master
                if not linked_raw_titles:
                    await self._title_repository.delete_master_title(master_title_id)
                    return

                # Re-merge the remaining clean titles
                merged_title = linked_raw_titles[0]
                for raw_title in linked_raw_titles[1:]:
                    merged_title = TitleMerger().merge(merged_title, raw_title)

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

    async def _detach_problematic_titles(self, raw_titles: list[TitleData], conflicting_mal_id: int) -> list[TitleData]:
        problematic_raw_titles = []
        clean_raw_titles = []
        for raw_title in raw_titles:
            if raw_title.mal_id == conflicting_mal_id:
                problematic_raw_titles.append(raw_title)
            else:
                clean_raw_titles.append(raw_title)

        if problematic_raw_titles:
            problematic_ids = [rt.id for rt in problematic_raw_titles if rt.id]
            await self._title_repository.unlink_raw_titles(problematic_ids)
            for rt_id in problematic_ids:
                await self._title_repository.update_consolidation_status(
                    raw_title_id=rt_id,
                    status=ConsolidationStatus.PENDING,
                    detail="Detached due to mal_id conflict"
                )

        return clean_raw_titles
