from pydantic import BaseModel

class PaginationItems(BaseModel):
    count: int = 0
    total: int = 0
    per_page: int = 0

class Pagination(BaseModel):
    last_visible_page: int = 0
    has_next_page: bool = False
    current_page: int = 0
    items: PaginationItems = PaginationItems()

    class Config:
        from_attributes = True