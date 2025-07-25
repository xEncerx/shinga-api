from datetime import datetime, timedelta
from pathlib import Path
import aiosqlite
import asyncio

from app.infrastructure.db.models import SourceProvider
from app.core import settings, logger


class TaskManager:
    """Manager for tracking parsing tasks and their progress."""

    def __init__(self) -> None:
        self.db_path = Path(settings.TEMP_PATH) / "db" / "task_manager.db"
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the task manager database."""
        await self._ensure_db_exists()
        await self._create_tables()
        logger.info("PageTracker initialized")

    async def _ensure_db_exists(self) -> None:
        """Ensure the database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def _create_tables(self) -> None:
        """Create necessary tables."""
        if not self.db_path.exists():
            with open(self.db_path, "w"):
                ...

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS parsed_pages (
                    provider TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (provider, page_number)
                )
                """
            )
            await db.commit()

    async def mark_page_completed(self, provider: SourceProvider, page: int) -> None:
        """Mark a page as completed for a provider."""
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO parsed_pages (provider, page_number)
                    VALUES (?, ?)
                    """,
                    (provider.name, page),
                )
                await db.commit()

    async def get_completed_pages(
        self,
        provider: SourceProvider,
        min_age: timedelta = timedelta(days=3),
    ) -> list[int]:
        """Get list of completed pages for a provider within the specified time frame."""
        cutoff_date = datetime.now() - min_age

        # Cleanup old records before fetching completed pages
        await self.cleanup_old_records(min_age)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT page_number FROM parsed_pages 
                WHERE provider = ? AND datetime(parsed_at) > datetime(?)
                ORDER BY page_number
                """,
                (provider.name, cutoff_date.strftime("%Y-%m-%d %H:%M:%S")),
            )

            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def cleanup_old_records(
        self,
        min_age: timedelta = timedelta(days=3),
    ) -> None:
        """Remove old records beyond the specified age."""
        cutoff_date = datetime.now() - min_age

        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    DELETE FROM parsed_pages WHERE datetime(parsed_at) < datetime(?)
                    """,
                    (cutoff_date.strftime("%Y-%m-%d %H:%M:%S"),),
                )
                await db.commit()

        logger.info(f"Cleaned up records older than {min_age}.")
