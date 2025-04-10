from fastapi import APIRouter, HTTPException, Request, Query
from fastapi_cache.decorator import cache

from app.utils.sorter import manga_sorter, SorterEnum
from app.services.manga_api import manga_api
from app.core import limiter, MC
from app.api.deps import CurrentUserDep
from app.core.database import *

router = APIRouter(prefix=f"/titles", tags=["titles"])


@router.get("/global-search")
@cache(expire=60 * 30)
@limiter.limit("30/minute")
async def search(
    query: str,
    limit: int = Query(default=1, ge=1, le=20),
    sortBy: SorterEnum = SorterEnum.BY_NAME,
    reverse: bool = False,
    *,
    user: CurrentUserDep,
    request: Request,
) -> MangaResponse:
    """
    Description: Global search from all available sources \n
    Limits: 30 requests per minute
    """

    if sortBy is SorterEnum.BY_DATE:
        raise HTTPException(
            status_code=400,
            detail="Sorting by date is not supported for global search",
        )

    response = await manga_api.search(query=query, limit=limit)

    user_mangas = get_user_manga(user_id=user.id)

    if user_mangas:
        user_manga_dict = {m.id: m for m in user_mangas}

        for index, manga in enumerate(response.content):
            source_code = f"{manga.source_name}|{manga.source_id}"
            if source_code in user_manga_dict:
                response.content[index] = user_manga_dict[source_code]

    response.content = manga_sorter.sort(
        manga_list=response.content,
        by=sortBy,
        extra_data=query,
        reverse=reverse,
    )

    return response


@router.get("/")
@cache(expire=60 * 30)
@limiter.limit("30/minute")
async def search_manga_by_id(
    query: str,
    source: MC.Sources,
    *,
    _: CurrentUserDep,
    request: Request,
) -> MangaResponse:
    """
    Description: Search title by slug or id \n
    Limits: 30 requests per minute
    """
    response = await manga_api.search_by_source(query=query, source=source)

    return response


@router.post("/create")
@limiter.limit("30/minute")
async def create_manga(
    manga: Mangas,
    _: CurrentUserDep,
    request: Request,
) -> Message:
    """
    Description: Create title \n
    Limits: 30 requests per minute
    """

    if is_manga_exists(manga_id=manga.id):
        raise HTTPException(
            status_code=409,
            detail="Manga already exists",
        )

    success = add_manga(data=manga)

    if success:
        return Message(
            message="Manga created successfully",
        )

    raise HTTPException(
        status_code=500,
        detail="Failed to create manga",
    )


@router.put("/me/update")
@limiter.limit("30/minute")
async def update_user_manga(
    manga: UpdateUserManga,
    user: CurrentUserDep,
    request: Request,
) -> Message:
    """
    Description: Update the title data in the user's list \n
    Limits: 30 requests per minute
    """

    if not is_manga_exists(manga.manga_id):
        raise HTTPException(
            status_code=404,
            detail="Manga not found",
        )

    success = upsert_user_manga(
        user_id=user.id,
        data=manga,
    )
    if success:
        return Message(
            message="Your manga data updated successfully",
        )

    raise HTTPException(
        status_code=500,
        detail="Failed to update manga",
    )


@router.get("/me")
@limiter.limit("60/minute")
async def get_all_user_manga(
    sortBy: SorterEnum = SorterEnum.BY_DATE,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    section: MC.Section = MC.Section.ANY,
    *,
    user: CurrentUserDep,
    request: Request,
) -> MangaResponse:
    """
    Description: Getting all user titles \n
    Limits: 60 requests per minute
    """
    if sortBy is SorterEnum.BY_NAME:
        raise HTTPException(
            status_code=400,
            detail="Sorting by name is not supported for user manga",
        )

    user_mangas = get_user_manga(user_id=user.id, section=section)
    user_mangas = manga_sorter.sort(user_mangas, by=sortBy)

    total_items = len(user_mangas)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_mangas = user_mangas[start_idx:end_idx]

    return MangaResponse(
        message=f"Total pages: {(total_items + per_page - 1) // per_page}",
        content=paginated_mangas,
    )


@router.get("/suggest")
@cache(expire=60 * 30)
async def suggest_name(
    query: str,
    source: MC.Sources = MC.Sources.MANGA_POISK,
    *,
    _: CurrentUserDep,
) -> MangaResponse:
    """
    Description: Getting suggestions for the entered name
    """
    response = await manga_api.suggest(query=query, source=source)

    return response
