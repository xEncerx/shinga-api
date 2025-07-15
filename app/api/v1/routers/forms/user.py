from fastapi import APIRouter

from app.api.v1.schemas import *

router = APIRouter(prefix="/users")

@router.get("/bookmarks")
async def get_types() -> BookMarksForm:
    return BookMarksForm(
        bookmarks=[
            i.value for i in BookMarkType
        ]
    )