from fastapi import APIRouter, Request

from src.presentation.api.dependencies.rate_limit import limiter
from src.domain.models.titles import (
    TitleGenre,
    TitleCategory,
    TitleType,
    TitleStatus,
    TitleBookmark,
)
from src.presentation.api.decorators.cache_control_route import *
from src.presentation.api.schemas.responses.forms import *

router = APIRouter(
    prefix="/titles",
    route_class=cache_control_route(),
    tags=["Titles Forms"],
)


@router.get("/genres")
@limiter.limit("60/minute")
async def get_genres_endpoint(request: Request) -> TitleGenresResponse:
    """Get list of available title genres"""
    genres = TitleGenresResponse(
        content=[
            TitleGenreForm(
                name=genre.name,
                ru=genre.ru,
                en=genre.en,
            )
            for genre in TitleGenre
        ]
    )
    return genres


@router.get("/categories")
@limiter.limit("60/minute")
async def get_categories_endpoint(request: Request) -> TitleCategoriesResponse:
    """Get list of available title categories"""
    categories = TitleCategoriesResponse(
        content=[
            TitleCategoryForm(
                name=category.name,
                ru=category.ru,
                en=category.en,
            )
            for category in TitleCategory
        ]
    )
    return categories


@router.get("/statuses")
@limiter.limit("60/minute")
async def get_statuses_endpoint(request: Request) -> TitleStatusesResponse:
    """Get list of available title statuses"""
    statuses = TitleStatusesResponse(
        content=[
            TitleStatusForm(
                name=status.name,
            )
            for status in TitleStatus
        ]
    )
    return statuses


@router.get("/types")
@limiter.limit("60/minute")
async def get_types_endpoint(request: Request) -> TitleTypesResponse:
    """Get list of available title types"""
    types = TitleTypesResponse(
        content=[
            TitleTypeForm(
                name=type_.name,
            )
            for type_ in TitleType
        ]
    )
    return types


@router.get("/bookmarks")
@limiter.limit("60/minute")
async def get_bookmarks_endpoint(request: Request) -> TitleBookmarksResponse:
    """Get list of available title bookmarks"""
    bookmarks = TitleBookmarksResponse(
        content=[
            TitleBookmarkForm(
                name=bookmark.name,
            )
            for bookmark in TitleBookmark
        ]
    )
    return bookmarks
