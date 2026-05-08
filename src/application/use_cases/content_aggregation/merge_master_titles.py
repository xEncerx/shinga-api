from src.domain.errors import RecordNotFoundError, ValidationError
from src.domain.interfaces import ITitleRepository


class MergeMasterTitlesUseCase:
    def __init__(self, title_repository: ITitleRepository) -> None:
        self._title_repository = title_repository

    async def execute(self, target_id: int, source_id: int) -> None:
        """Merge the source title into the target title."""
        if target_id == source_id:
            raise ValidationError("Cannot merge a title with itself.")

        target_title = await self._title_repository.get_master_title(target_id)
        source_title = await self._title_repository.get_master_title(source_id)

        if not target_title or not source_title:
            raise RecordNotFoundError(
                f"Cannot merge: target {target_id} or source {source_id} not found."
            )

        await self._title_repository.merge_master_titles(
            target_id=target_id, source_id=source_id
        )
