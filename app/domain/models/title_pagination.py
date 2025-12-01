from typing import Generic, TypeVar
from pydantic import BaseModel

from .pagination import Pagination

T = TypeVar("T")


class TitlePagination(BaseModel, Generic[T]):
    pagination: Pagination = Pagination()
    data: list[T] = []
