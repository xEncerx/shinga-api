from dataclasses import dataclass

from src.domain.interfaces import ITitleRepository, IBaseMatcher
from src.domain.services import (
    TitleSimilarityScorer,
    TitleMerger,
    TextNormalizer,
    TitleQualityScorer,
)
from src.domain.models import (
    SourceTitleData,
    TitleData,
    TitleCover,
    ConsolidationStatus,
    Source,
)


@dataclass
class ConsolidationResult:
    raw_title_id: int
    master_title_id: int
    external_id: str
    source: Source
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
        # 1. Retrieve the raw title
        raw_title = await self._title_repository.get_raw_title(raw_title_id)
        if not raw_title:
            raise ValueError(f"Raw title with ID {raw_title_id} not found.")

        cover_url = raw_title.title_data.cover.original

        # 2. Attempt to find a matching master title and consolidate it, or create a new master title if no match is found
        master_title_id, is_new = await self._upsert_title(raw_title)

        # 3. Link raw title to master title
        await self._title_repository.link_raw_to_master(
            raw_title_id=raw_title_id,
            master_title_id=master_title_id,  # type: ignore
        )
        # 4. Update status to CONSOLIDATED
        await self._title_repository.update_consolidation_status(
            raw_title_id=raw_title_id,
            status=ConsolidationStatus.CONSOLIDATED,
        )

        return ConsolidationResult(
            raw_title_id=raw_title_id,
            master_title_id=master_title_id,  # type: ignore
            external_id=raw_title.source_metadata.external_id,
            source=raw_title.source_metadata.source,
            is_new=is_new,
            cover_url=cover_url,
        )

    async def _upsert_title(self, raw_title: SourceTitleData) -> tuple[int, bool]:
        rtd = raw_title.title_data
        is_new = False

        # 1. Try to find a matching master title using matchers
        candidate = await self._find_candidate(raw_title)
        # If candidate is found, update it with merged data from raw title and candidate
        if candidate:
            master_title_id = await self._update_existing_title(
                master_title_id=candidate.id,  # type: ignore
                raw_title=raw_title,
                candidate=candidate,
            )
            return master_title_id, is_new

        # 2. If no candidate found, create a new master title based on raw title data
        lock_key = self._generate_lock_key(rtd)
        async with self._title_repository.lock(lock_key):  # type: ignore
            # Re-check inside the lock: another worker may have created the title
            # while this worker was waiting to acquire the lock
            # 2.1 Try to find a candidate again to avoid duplicates
            candidate = await self._find_candidate(raw_title)
            if candidate:
                master_title_id = await self._update_existing_title(
                    master_title_id=candidate.id,  # type: ignore
                    raw_title=raw_title,
                    candidate=candidate,
                )
            else:
                # 2.2 If still no candidate, create a new master title
                master_title_id = await self._add_new_title(raw_title=raw_title)
                is_new = True

        return master_title_id, is_new

    async def _add_new_title(self, raw_title: SourceTitleData) -> int:
        raw_title.title_data.cover = TitleCover.pending()
        rtd = raw_title.title_data

        return await self._title_repository.add_master_title(
            raw_title,
            search_text=self._text_normalizer.normalize_multiple(
                [rtd.name_ru, rtd.name_en, *rtd.alt_names],
            ),
            data_quality_score=self._quality_scorer.score(rtd),
        )

    def _generate_lock_key(self, title_data: TitleData) -> str:
        """
        Generate a lock key for a raw title based on its MAL ID if available, or a normalized combination of its names otherwise.
        """
        if title_data.mal_id is not None:
            return f"consolidate:mal_id:{title_data.mal_id}"
        return "consolidate:" + self._text_normalizer.normalize_multiple(
            [title_data.name_ru, title_data.name_en, *title_data.alt_names],
        )

    async def _update_existing_title(
        self,
        master_title_id: int,
        raw_title: SourceTitleData,
        candidate: TitleData,
    ) -> int:
        merged_title = self._title_merger.merge(raw_title.title_data, candidate)
        await self._title_repository.update_master_title(
            master_title_id=master_title_id,
            title_data=merged_title,
            search_text=self._text_normalizer.normalize_multiple(
                [merged_title.name_ru, merged_title.name_en, *merged_title.alt_names],
            ),
            data_quality_score=self._quality_scorer.score(merged_title),
        )

        return candidate.id  # type: ignore

    async def _find_candidate(
        self,
        raw_title: SourceTitleData,
    ) -> TitleData | None:
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
    ) -> TitleData | None:
        for matcher in self._definitive_matchers:
            candidates = await matcher.find_candidates(raw_title)
            if candidates:
                return candidates[0]  # Return the first definitive match
        return None

    async def _try_other_matchers(self, raw_title: SourceTitleData) -> TitleData | None:
        best_candidate = None
        highest_score = 0.0

        for matcher in self._other_matchers:
            candidates = await matcher.find_candidates(raw_title)
            for candidate in candidates:
                score = self._similarity_scorer.score(raw_title.title_data, candidate)
                if score > highest_score and score >= self.SIMILARITY_THRESHOLD:
                    highest_score = score
                    best_candidate = candidate

        return best_candidate
