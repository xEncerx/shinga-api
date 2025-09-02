from app.infrastructure.db.repositories.title_repository import *
from app.api.v1.schemas import (
    TitlePaginationResponse,
    TitleWithUserData,
    TitlePublic,
    UserTitlePublic,
    TitleSearchFields,
)
from app.infrastructure.db.models import TitleGenre

class TitleSearchService:
    @staticmethod
    def _normalize_genres(genres: list[str] | None) -> list[TitleGenre] | None:
        if not genres:
            return None
        
        result = []
        for name in set(genres):
            genre = TitleGenre.get(en=name, ru=name)
            if genre:
                result.append(genre)
        return result or None

    @classmethod
    async def search(
        cls,
        params: TitleSearchFields,
        *,
        username: str | None,
        mode: TitleSearchMode = TitleSearchMode.GLOBAL,
    ) -> TitlePaginationResponse:
        data = params.model_dump()
        data["genres"] = cls._normalize_genres(data.get("genres"))

        repo_result = await TitleRepository.search(
            mode=mode,
            username=username,
            **data,
        )

        return TitlePaginationResponse(
            pagination=Pagination.model_validate(repo_result["pagination"]),
            content=[
                TitleWithUserData(
                    title=TitlePublic.model_validate(item["title"]),
                    user_data=(
                        UserTitlePublic.model_validate(item["user_data"])
                        if item["user_data"]
                        else None
                    ),
                )
                for item in repo_result["content"]
            ],
        )