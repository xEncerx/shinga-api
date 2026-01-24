# Adding a New Source

This guide walks through integrating a new manga source into the system.

## Overview

A source integration consists of two main components:

- **Client**: Handles API requests and responses
- **Parser**: Transforms API data into application data structures

## Implementation Steps

### 1. Create Source Directory Structure

Copy the `custom` template directory as your base:
```
src/infrastructure/sources/
├── your_source/
│   ├── __init__.py
│   ├── client.py
│   └── parser.py
```

### 2. Implement the Client

Edit `your_source/client.py` and customize the following:

#### Required Constants

```python
BASE_URL = "https://your-api.com/api/"
REQUESTS_PER_SECOND = 3.0
```

- **BASE_URL**: The base URL for API requests
- **REQUESTS_PER_SECOND**: Request rate limit (enforced by AsyncHttpClient with aiolimiter)

#### Required Methods

**`get_by_id(external_id: str) -> SourceTitleData | None`**

Fetch a single title by its external ID. Return `None` if not found.

Example:
```python
async def get_by_id(self, external_id: str) -> SourceTitleData | None:
    async with self.get(f"manga/{external_id}") as response:
        data = await response.json()
        return CustomParser.parse_title(data["data"]) if "data" in data else None
```

**`get_page(page: int = 1, limit: int = 25) -> list[SourceTitleData]`**

Fetch a catalog page. Return an empty list if no data is available.

```python
async def get_page(self, page: int = 1, limit: int = 25) -> list[SourceTitleData]:
    async with self.get("manga", params={"page": page, "limit": limit}) as response:
        data = await response.json()
        return CustomParser.parse_page(data) if data.get("data") else []
```

**`get_source_detail() -> SourceDetail`**

Return source metadata including total pages and items per page.

```python
async def get_source_detail(self) -> SourceDetail:
    return SourceDetail(
        source=Source.YOUR_SOURCE,
        total_pages=1000,
        items_per_page=30,
    )
```

#### Exception Handling

> Do not catch exceptions in client methods. The base class handles all error processing.

### 3. Implement the Parser

Edit `your_source/parser.py` and provide:

#### Main Method

**`parse_title(data: dict) -> SourceTitleData`**

Convert API response data into a `SourceTitleData` object.

Key points:
- Remove fields your source doesn't provide
- Use `tag_remover()` utility for HTML-encoded descriptions
- Convert dates to timezone-naive `datetime` objects
- Convert genre, type, status, and category values using mapping dictionaries
- Select the highest-resolution cover image available

```python
@staticmethod
def parse_title(data: dict) -> SourceTitleData:
    source_metadata = SourceMetadata(
        source=Source.YOUR_SOURCE,
        external_id=str(data["id"]),
        source_url=data.get("url"),
    )
    
    title_data = TitleData(
        name_ru=data["name_ru"],
        name_en=data["name_en"],
        description_ru=tag_remover(data["description_ru"]),
        type=YourParser.convert_type(data["type"]),
        status=YourParser.convert_status(data["status"]),
        # ... additional fields
        genres=[YourParser.convert_genre(g) for g in data["genres"]],
        categories=[YourParser.convert_category(c) for c in data["categories"]],
        cover=TitleCover(
            thumbnail=data["images"]["small"],
            original=data["images"]["large"],
        ),
    )
    
    return SourceTitleData(
        source_metadata=source_metadata,
        title_data=title_data,
    )
```

#### Page Parsing

**`parse_page(data: dict) -> list[SourceTitleData]`**

Parse catalog pages. Catch and log errors to prevent entire pages from failing.

#### Mapping Dictionaries

Define conversion mappings for your source values:

```python
_GENRE_MAPPING: dict[str, TitleGenre] = {
    "action": TitleGenre.ACTION,
    "comedy": TitleGenre.COMEDY,
    # ...
}

_TYPE_MAPPING: dict[str, TitleType] = {
    "manga": TitleType.MANGA,
    "manhwa": TitleType.MANHWA,
    # ...
}

_STATUS_MAPPING: dict[str, TitleStatus] = {
    "publishing": TitleStatus.ONGOING,
    "finished": TitleStatus.COMPLETED,
    # ...
}

_CATEGORY_MAPPING: dict[str, TitleCategory] = {
    "shounen": TitleCategory.SHOUNEN,
    # ...
}
```

### 4. Register the Source

**In `src/domain/models/source.py`:**

Add your source to the `Source` enum:

```python
class Source(str, Enum):
    # ... existing sources
    YOUR_SOURCE = "your_source"
```

**In `src/infrastructure/sources/__init__.py`:**

Import and add your client to `AVAILABLE_SOURCES`:

```python
from .your_source.client import YourSourceClient

AVAILABLE_SOURCES = {
    Source.MAL: MalClient,
    Source.REMANGA: RemangaClient,
    # ...
    Source.YOUR_SOURCE: YourSourceClient,
}
```

### 5. Create Database Migration

Generate an automatic migration:

```bash
alembic revision --autogenerate -m "add_source_YOUR_SOURCE"
```

Apply the migration:

```bash
alembic upgrade head
```

## Testing

After implementation, test basic functionality:

1. Fetch a single title by ID
2. Fetch a catalog page
3. Verify data parsing and mapping
4. Confirm database operations

## Related Files

- Template Implementation: [custom/](./custom/)
- Base Client: [base_provider.py](./base_provider.py)
- Base Parser: [base_parser.py](./base_parser.py)
- Source Registry: [source_manager.py](./source_manager.py)
