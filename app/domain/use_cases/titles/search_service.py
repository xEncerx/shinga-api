from app.domain.enums import TitleGenre
from app.infrastructure.db import (
    TitleCRUD,
    TitleSearchMode,
)
from app.api.v1.schemas import (
    TitlePaginationResponse,
    TitleSearchResponse,
    TitleWithUserData,
    TitlePublic,
    UserTitlePublic,
    TitleSearchFields,
)
from app.domain.models import Pagination


class TitleSearchService:
    @staticmethod
    def _normalize_genres(genres: list[str] | None) -> list[TitleGenre] | None:
        """
        Normalize genre names to TitleGenre objects.

        Args:
            genres (list[str] | None): List of genre names.
        Returns:
            list[TitleGenre] | None: List of TitleGenre objects or None if no valid genres are found.
        """
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
        user_id: int | None,
        mode: TitleSearchMode = TitleSearchMode.GLOBAL,
    ) -> TitlePaginationResponse:
        """
        Search for titles based on the given parameters.
        """
        data = params.model_dump()
        data["genres"] = cls._normalize_genres(data.get("genres"))

        result = await TitleCRUD.read.search(
            mode=mode,
            user_id=user_id,
            **data,
        )

        return TitlePaginationResponse(
            pagination=Pagination.model_validate(result["pagination"]),
            content=[
                TitleWithUserData(
                    title=TitlePublic.model_validate(item["title"]),
                    user_data=(
                        UserTitlePublic.model_validate(item["user_data"])
                        if item["user_data"]
                        else None
                    ),
                )
                for item in result["content"]
            ],
        )

    @staticmethod
    async def get_recommendations(
        title_id: int,
        user_id: int | None = None,
        limit: int = 20,
    ) -> TitleSearchResponse:
        """
        Get recommendations for a title based on user preferences.
        Based on genre, type, rating similarity and popularity.

        Args:
            title_id (int): The ID of the source title.
            user_id (int | None): The user ID for user-specific data.
            limit (int): Number of recommendations to return.

        Returns:
            TitleSearchResponse: A list of recommended titles with user data.
        """
        result = await TitleCRUD.read.recommendations(
            title_id=title_id,
            user_id=user_id,
            limit=limit,
        )

        return TitleSearchResponse(
            content=[
                TitleWithUserData(
                    title=TitlePublic.model_validate(item["title"]),
                    user_data=(
                        UserTitlePublic.model_validate(item["user_data"])
                        if item["user_data"]
                        else None
                    ),
                )
                for item in result["content"]
            ],
        )

    @staticmethod
    async def get_title_by_id(
        title_id: int,
        user_id: int | None = None,
    ) -> TitleWithUserData | None:
        """
        Get a title by its ID, including user-specific data if a user ID is provided.

        Args:
            title_id (int): The ID of the title to retrieve.
            user_id (int | None): The user ID for user-specific data.
        Returns:
            TitleWithUserData | None: The title with user data or None if not found.
        """
        result = await TitleCRUD.read.with_user_data(
            title_id=title_id,
            user_id=user_id,
        )
        if not result or not result.get("title"):
            return None

        return TitleWithUserData(
            title=TitlePublic.model_validate(result["title"]),
            user_data=(
                UserTitlePublic.model_validate(result["user_data"])
                if result["user_data"]
                else None
            ),
        )
