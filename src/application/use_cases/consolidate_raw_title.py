from dataclasses import dataclass

from src.domain.interfaces import ITitleRepository, IBaseMatcher
from src.domain.services import (
    TitleSimilarityScorer,
    TitleMerger,
    TextNormalizer,
    TitleQualityScorer,
)
from src.domain.models.titles import SourceTitleData, TitleData, TitleCover
from src.domain.models.services import ConsolidationStatus


@dataclass
class ConsolidationResult:
    raw_title_id: int
    master_title_id: int
    external_id: str
    source: str
    is_new: bool
    cover_url: str | None = None


class ConsolidateRawTitleUseCase:
    SIMILARITY_THRESHOLD = 85

    def __init__(
        self,
        title_repository: ITitleRepository,
        matchers: list[IBaseMatcher],
        similarity_scorer: TitleSimilarityScorer = TitleSimilarityScorer(),
        title_merger: TitleMerger = TitleMerger(),
        text_normalizer: TextNormalizer = TextNormalizer(),
        quality_scorer: TitleQualityScorer = TitleQualityScorer(),
    ):
        self._title_repository = title_repository
        self._matchers = matchers
        self._similarity_scorer = similarity_scorer
        self._title_merger = title_merger
        self._text_normalizer = text_normalizer
        self._quality_scorer = quality_scorer

        if len(matchers) == 0:
            raise ValueError("At least one matcher must be provided.")

        self._definitive_matchers = [m for m in matchers if m.is_definitive]
        self._other_matchers = [m for m in matchers if not m.is_definitive]

    async def execute(self, raw_title_id: int) -> ConsolidationResult:
        """
        Consolidate a raw title into a master title, merging if a match is found or creating a new one.

        Args:
            raw_title_id (int): The ID of the raw title to consolidate.
        """
        is_new = False

        # 1. Retrieve the raw title
        raw_title = await self._title_repository.get_raw_title(raw_title_id)
        if not raw_title:
            raise ValueError(f"Raw title with ID {raw_title_id} not found.")

        cover_url = raw_title.title_data.cover.original

        # 2. Update status to IN_PROGRESS
        # await self._title_repository.update_consolidation_status(
        #     raw_title_id=raw_title_id,
        #     status=ConsolidationStatus.IN_PROGRESS,
        # )

        candidate = await self._find_candidate(raw_title)

        # 3. Merge or create title
        if candidate:
            # Match found = merge titles
            merged_title = self._title_merger.merge(raw_title.title_data, candidate[0])
            await self._title_repository.update_master_title(
                master_title_id=candidate[1],
                title_data=merged_title,
                search_text=self._text_normalizer.normalize_multiple(
                    [
                        merged_title.name_ru,
                        merged_title.name_en,
                        *merged_title.alt_names,
                    ],
                    deduplicate=True,
                    min_word_length=3,
                ),
                data_quality_score=self._quality_scorer.score(merged_title),
            )
            master_title_id = candidate[1]
        else:
            # No match found = create a new title

            # Use pending cover for new titles to download later
            raw_title.title_data.cover = TitleCover.pending()
            td = raw_title.title_data
            master_title_id = await self._title_repository.add_master_title(
                raw_title,
                search_text=self._text_normalizer.normalize_multiple(
                    [td.name_ru, td.name_en, *td.alt_names],
                    deduplicate=True,
                    min_word_length=3,
                ),
                data_quality_score=self._quality_scorer.score(td),
            )
            is_new = True
        # 4. Link raw title to master title
        await self._title_repository.link_raw_to_master(
            raw_title_id=raw_title_id,
            master_title_id=master_title_id,
        )
        # 5. Update status to CONSOLIDATED
        await self._title_repository.update_consolidation_status(
            raw_title_id=raw_title_id,
            status=ConsolidationStatus.CONSOLIDATED,
        )

        return ConsolidationResult(
            raw_title_id=raw_title_id,
            master_title_id=master_title_id,
            external_id=raw_title.source_metadata.external_id,
            source=raw_title.source_metadata.source.value,
            is_new=is_new,
            cover_url=cover_url,
        )

    async def _find_candidate(
        self,
        raw_title: SourceTitleData,
    ) -> tuple[TitleData, int] | None:
        # Try definitive matchers first (100% confidence)
        if len(self._definitive_matchers) > 0:
            candidate = await self._try_definitive_matchers(raw_title)
            if candidate:
                return candidate

        if len(self._other_matchers) > 0:
            # If no definitive match, try other matchers
            return await self._try_other_matchers(raw_title)

        return None

    async def _try_definitive_matchers(
        self, raw_title: SourceTitleData
    ) -> tuple[TitleData, int] | None:
        for matcher in self._definitive_matchers:
            candidates = await matcher.find_candidates(raw_title)
            if candidates:
                return candidates[0]  # Return the first definitive match
        return None

    async def _try_other_matchers(
        self, raw_title: SourceTitleData
    ) -> tuple[TitleData, int] | None:
        best_candidate = None
        highest_score = 0.0

        for matcher in self._other_matchers:
            candidates = await matcher.find_candidates(raw_title)
            for candidate in candidates:
                score = self._similarity_scorer.score(
                    raw_title.title_data, candidate[0]
                )
                if score > highest_score and score >= self.SIMILARITY_THRESHOLD:
                    highest_score = score
                    best_candidate = candidate

        return best_candidate
