from fastapi import APIRouter

from src.domain.models.titles import TitleGenre, TitleCategory, TitleType, TitleStatus
from src.presentation.api.schemas.responses.forms import *

router = APIRouter(prefix="/titles", tags=["Titles Forms"])


@router.get("/genres")
async def get_genres_endpoint() -> TitleGenresResponse:
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
async def get_categories_endpoint() -> TitleCategoriesResponse:
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
async def get_statuses_endpoint() -> TitleStatusesResponse:
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
async def get_types_endpoint() -> TitleTypesResponse:
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
