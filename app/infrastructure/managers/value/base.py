from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any
from enum import Enum
import aiosqlite
import aiofiles
import asyncio
import time

from app.core import logger


class ValueStatus(Enum):
    """Status enumeration for managed values"""

    ACTIVE = "active"
    COOLING = "cooling"


@dataclass
class Limit:
    """Represents a rate limit configuration"""

    name: str
    max_requests: int
    time_window: int  # seconds
    cooldown: int  # seconds


@dataclass
class UsageRecord:
    """Tracks usage for a specific limit"""

    timestamps: list[float] = field(default_factory=list)
    last_reset: float = field(default_factory=time.time)


class BaseValueManager(ABC):
    """
    Abstract base class for managing values (proxies, API keys, etc.) with rate limiting,
    automatic validation, and database persistence.

    This manager provides:
    - Database storage and retrieval
    - Rate limiting with multiple limits per value
    - Automatic validation scheduling
    - Cooling down mechanism for rate-limited values
    - Batch and sequential processing options
    """

    def __init__(
        self,
        validation_interval: int | None = None,
        fetch_interval: int | None = None,
        batch_validation: bool = False,
        batch_size: int = 10,
    ) -> None:
        """
        Initialize the base value manager.

        Args:
            db_path: Path to SQLite database file
            validation_interval: Interval in seconds for automatic validation (None to disable)
            fetch_interval: Interval in seconds for fetching new data (None to disable)
            batch_validation: Whether to use batch processing for validation
            batch_size: Size of batches for batch processing
        """
        self.validation_interval = validation_interval
        self.fetch_interval = fetch_interval
        self.batch_validation = batch_validation
        self.batch_size = batch_size

        # Get DB name from class name and set up database path
        self.db_name = self.__class__.__name__.lower()
        self.db_path = Path(__file__).parent.parent / "temp" / "db"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_path / f"{self.db_name}.db"

        # Rate limiting configuration
        self.limits: dict[str, Limit] = {}
        self.usage_tracking: dict[str, dict[str, UsageRecord]] = {}

        # Background tasks
        self._validation_task: asyncio.Task | None = None
        self._fetch_task: asyncio.Task | None = None
        self._running = False

    async def initialize(self) -> None:
        """Initialize the manager and start background tasks"""
        await self._init_database()
        self._running = True

        # Start background tasks
        if self.validation_interval:
            self._validation_task = asyncio.create_task(self._validation_scheduler())

        if self.fetch_interval:
            self._fetch_task = asyncio.create_task(self._fetch_scheduler())

        logger.info(f"{self.__class__.__name__} initialized successfully")

    async def cleanup(self) -> None:
        """Clean up resources and stop background tasks"""
        self._running = False

        if self._validation_task:
            self._validation_task.cancel()
            try:
                await self._validation_task
            except asyncio.CancelledError:
                pass

        if self._fetch_task:
            self._fetch_task.cancel()
            try:
                await self._fetch_task
            except asyncio.CancelledError:
                pass

        logger.info(f"{self.__class__.__name__} cleaned up")

    def add_limit(
        self, name: str, max_requests: int, time_window: int, cooldown: int
    ) -> None:
        """
        Add a rate limit configuration.

        Args:
            name: Unique name for the limit
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
            cooldown: Cooldown period in seconds after limit is reached
        """
        self.limits[name] = Limit(name, max_requests, time_window, cooldown)
        logger.info(
            f"{self.__class__.__name__}: Added limit '{name}': {max_requests} requests per {time_window}s, cooldown {cooldown}s"
        )

    async def _init_database(self) -> None:
        """Initialize database table for this manager"""
        if not self.db_path.exists():
            async with aiofiles.open(self.db_path, mode="w") as f:
                pass

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS value_manager (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT '{ValueStatus.ACTIVE.value}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    cooldown_until TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
                """
            )

            await db.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_value_manager_status 
                ON value_manager(status)
                """
            )
            await db.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_value_manager_status_cooldown 
                ON value_manager(status, cooldown_until)
                """
            )

            await db.commit()

    async def _validation_scheduler(self) -> None:
        """Background task for periodic validation"""
        while self._running:
            try:
                await asyncio.sleep(self.validation_interval)  # type: ignore
                if self._running:
                    logger.info("Running scheduled validation...")
                    await self.validate_values()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in validation scheduler: {e}")
                await asyncio.sleep(min(60, self.validation_interval))  # type: ignore

    async def _fetch_scheduler(self) -> None:
        """Background task for periodic data fetching"""
        while self._running:
            try:
                await asyncio.sleep(self.fetch_interval)  # type: ignore
                if self._running:
                    logger.info("Running scheduled data fetch...")
                    await self.fetch_and_store_values()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in fetch scheduler: {e}")

    async def get_value(self, auto_mark_as_used: bool = True) -> str | None:
        """
        Get an available value that's not in cooldown and hasn't exceeded limits.

        Args:
            auto_mark_as_used: Whether to automatically mark the value as used

        Returns:
            Available value string or None if no values are available
        """
        # First, update cooling statuses
        await self._update_cooling_statuses()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                f"""
                SELECT value FROM value_manager 
                WHERE status = '{ValueStatus.ACTIVE.value}'
                ORDER BY usage_count ASC, last_used ASC
                LIMIT 1
                """
            )

            rows = await cursor.fetchall()

            for row in rows:
                value = row[0]
                if await self._can_use_value(value):
                    # Auto mark as used if requested
                    if auto_mark_as_used:
                        await self.mark_as_used(value)

                    return value

        return None

    async def mark_as_used(self, value: str) -> bool:
        """
        Mark a value as used and update rate limiting tracking.

        Args:
            value: The value that was used

        Returns:
            True if marking was successful, False otherwise
        """
        current_time = time.time()

        # Initialize usage tracking for this value if not exists
        if value not in self.usage_tracking:
            self.usage_tracking[value] = {}

        # Update usage for each limit
        needs_cooling = False
        cooldown_until = 0

        for limit_name, limit in self.limits.items():
            if limit_name not in self.usage_tracking[value]:
                self.usage_tracking[value][limit_name] = UsageRecord()

            usage_record = self.usage_tracking[value][limit_name]

            # Clean old timestamps outside the time window
            cutoff_time = current_time - limit.time_window
            usage_record.timestamps = [
                ts for ts in usage_record.timestamps if ts > cutoff_time
            ]

            # Add current usage
            usage_record.timestamps.append(current_time)

            # Check if limit is exceeded
            if len(usage_record.timestamps) >= limit.max_requests:
                needs_cooling = True
                limit_cooldown_until = current_time + limit.cooldown
                cooldown_until = max(cooldown_until, limit_cooldown_until)

        # Update database
        status = (
            ValueStatus.COOLING.value if needs_cooling else ValueStatus.ACTIVE.value
        )
        cooldown_timestamp = (
            datetime.fromtimestamp(cooldown_until) if needs_cooling else None
        )

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                UPDATE value_manager
                SET last_used = CURRENT_TIMESTAMP, 
                    usage_count = usage_count + 1,
                    status = ?,
                    cooldown_until = ?
                WHERE value = ?
                """,
                (status, cooldown_timestamp, value),
            )
            await db.commit()

        if needs_cooling:
            logger.info(
                f"Value {value} sent to cooling until {datetime.fromtimestamp(cooldown_until)}"
            )

        return True

    async def _can_use_value(self, value: str) -> bool:
        """Check if a value can be used based on rate limits"""
        if value not in self.usage_tracking:
            return True

        current_time = time.time()

        for limit_name, limit in self.limits.items():
            if limit_name not in self.usage_tracking[value]:
                continue

            usage_record = self.usage_tracking[value][limit_name]

            # Clean old timestamps
            cutoff_time = current_time - limit.time_window
            usage_record.timestamps = [
                ts for ts in usage_record.timestamps if ts > cutoff_time
            ]

            # Check if adding one more request would exceed the limit
            if len(usage_record.timestamps) >= limit.max_requests:
                return False

        return True

    async def _update_cooling_statuses(self) -> None:
        """Update status of values that finished cooling down"""
        current_time = datetime.now()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"""
                UPDATE value_manager
                SET status = '{ValueStatus.ACTIVE.value}' 
                WHERE status = '{ValueStatus.COOLING.value}' 
                AND cooldown_until <= ?
                """,
                (current_time,),
            )
            await db.commit()

    async def store_values(self, values: list[str]) -> None:
        """
        Store new values in the database, avoiding duplicates.

        Args:
            values: List of values to store
        """
        if not values:
            return

        stored_count = 0
        async with aiosqlite.connect(self.db_path) as db:
            for value in values:
                try:
                    await db.execute(
                        f"""
                        INSERT INTO value_manager (value, status) 
                        VALUES (?, '{ValueStatus.ACTIVE.value}')
                        """,
                        (value,),
                    )
                    stored_count += 1
                except aiosqlite.IntegrityError:
                    continue

            await db.commit()

        logger.info(f"Stored {stored_count} new values")

    async def remove_value(self, value: str) -> None:
        """Remove a value from the database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"DELETE FROM value_manager WHERE value = ?", (value,))
            await db.commit()

        # Also remove from usage tracking
        if value in self.usage_tracking:
            del self.usage_tracking[value]

    async def remove_values_batch(
        self,
        values: list[str],
        batch_size: int = 500,
    ) -> None:
        """Remove multiple values from the database in a single transaction"""
        if not values:
            return

        async with aiosqlite.connect(self.db_path) as db:
            for i in range(0, len(values), batch_size):
                batch = values[i : i + batch_size]
                placeholders = ",".join(["?" for _ in batch])
                await db.execute(
                    f"DELETE FROM value_manager WHERE value IN ({placeholders})",
                    batch,
                )
            await db.commit()

        # Also remove from usage tracking
        for value in values:
            if value in self.usage_tracking:
                del self.usage_tracking[value]

    async def get_stats(self) -> dict[str, Any]:
        """Get statistics with optimized query"""
        async with aiosqlite.connect(self.db_path) as db:
            # Одним запросом получаем все статистики
            cursor = await db.execute(
                f"""
                SELECT 
                    COUNT(*) as total_count,
                    SUM(CASE WHEN status = '{ValueStatus.ACTIVE.value}' THEN 1 ELSE 0 END) as active_count,
                    SUM(CASE WHEN status = '{ValueStatus.COOLING.value}' THEN 1 ELSE 0 END) as cooling_count
                FROM value_manager
                """
            )
            
            row = await cursor.fetchone()
            total_count, active_count, cooling_count = row if row else (0, 0, 0)

        return {
            "total_values": total_count,
            "active_values": active_count,
            "cooling_values": cooling_count,
            "limits_configured": len(self.limits),
        }

    async def validate_values(self) -> None:
        """Validate all stored values and remove invalid ones"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT value FROM value_manager")
            values = [row[0] for row in await cursor.fetchall()]

        if not values:
            logger.info("No values to validate")
            return

        logger.info(f"{self.__class__.__name__}: Validating {len(values)} values...")

        if self.batch_validation:
            await self._validate_values_batch(values)
        else:
            await self._validate_values_sequential(values)

    async def _validate_values_batch(self, values: list[str]) -> None:
        """Validate values in batches"""
        for i in range(0, len(values), self.batch_size):
            batch = values[i : i + self.batch_size]

            # Create validation tasks for the batch
            tasks = [self.validate_value(value) for value in batch]
            results = await asyncio.gather(*tasks)

            invalid_values = []

            # Process results
            for value, result in zip(batch, results):
                if isinstance(result, Exception) or not result:
                    invalid_values.append(value)

            # Remove invalid values
            if invalid_values:
                await self.remove_values_batch(invalid_values)

            logger.info(
                f"Processed batch {i // self.batch_size + 1} of {len(values) // self.batch_size + 1}"
            )

    async def _validate_values_sequential(self, values: list[str]) -> None:
        """Validate values one by one"""
        for value in values:
            try:
                if not await self.validate_value(value):
                    await self.remove_value(value)
            except Exception as e:
                await self.remove_value(value)

    async def fetch_and_store_values(self) -> None:
        """Fetch new values and store them"""
        try:
            new_values = await self.fetch_values()
            if new_values:
                await self.store_values(new_values)
                logger.info(f"{self.__class__.__name__}: Fetched and stored {len(new_values)} new values")
            else:
                logger.info(f"{self.__class__.__name__}: No new values fetched")
        except Exception as e:
            logger.error(f"Error fetching values: {e}")

    # Abstract methods to be implemented by subclasses
    @abstractmethod
    async def fetch_values(self) -> list[str]:
        """
        Fetch new values from external source.

        Returns:
            List of new values to store
        """
        pass

    @abstractmethod
    async def validate_value(self, value: str) -> bool:
        """
        Validate a single value.

        Args:
            value: Value to validate

        Returns:
            True if value is valid, False otherwise
        """
        pass
