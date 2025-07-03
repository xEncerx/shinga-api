from pydantic import BaseModel

from ...infrastructure.db.models import Title
from .pagination import Pagination

class TitlePagination(BaseModel):
    pagination: Pagination = Pagination()
    data: list[Title] = []