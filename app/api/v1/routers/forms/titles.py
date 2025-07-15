from fastapi import APIRouter

from app.api.v1.schemas import *

router = APIRouter(prefix="/titles")

@router.get("/genres")
async def get_genres() -> GenresForm:
    return GenresForm(
        genres=[
            i.value for i in TitleGenre
        ]
    )

@router.get("/types")
async def get_types() -> TypesForm:
    return TypesForm(
        types=[
            i.value for i in TitleType
        ]
    )

@router.get("/statuses")
async def get_statuses() -> StatusesForm:
    return StatusesForm(
        statuses=[
            i.value for i in TitleStatus
        ]
    )

