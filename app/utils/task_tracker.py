import aiosqlite

from app.core import settings

class TaskTracker:
    """TaskTracker is a utility class for tracking tasks in a SQLite database."""
    _initialized_tables: dict[str, bool] = {}
    _db_path = settings.TEMP_PATH / "db" / "task_tracker.db"

    @classmethod
    async def _init_database(cls, table: str) -> None:
        """Initialize the database and create the specified table if it does not exist."""
        if cls._initialized_tables.get(table):
            return
        
        cls._db_path.parent.mkdir(parents=True, exist_ok=True)
        if not cls._db_path.exists():
            with open(cls._db_path, 'w'):...

        async with aiosqlite.connect(cls._db_path) as db:
            await db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL
                )
                """
            )
            await db.commit()

        cls._initialized_tables[table] = True

    @classmethod
    async def mark_done(cls, task_id: int, table: str) -> None:
        """
        Mark a task as done by inserting its ID into the database.

        Args:
            task_id (int): The ID of the task to mark as done.
            table (str): The name of the table to insert the task ID.
        """
        
        await cls._init_database(table)

        async with aiosqlite.connect(cls._db_path) as db:
            await db.execute(
                f"INSERT OR IGNORE INTO {table} (task_id) VALUES (?)",
                (task_id,)
            )
            await db.commit()

    @classmethod
    async def get_missing_tasks(cls, need_range: range, table: str) -> set[int]:
        """
        Get the IDs of tasks that are not marked as done.
        
        Args:
            need_range (range): A range of task IDs to check.
            table (str): The name of the table to insert the task ID into.
        """
        await cls._init_database(table)

        async with aiosqlite.connect(cls._db_path) as db:
            cursor = await db.execute(
                f"SELECT task_id FROM {table}"
            )
            done_ids = {row[0] for row in await cursor.fetchall()}

        return set(need_range) - done_ids