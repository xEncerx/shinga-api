from datetime import datetime
from pathlib import Path
import subprocess
import os

from app.core.config import settings
from app.utils import logger


async def perform_backup_task() -> None:
    os.environ["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    backup_dir = Path(settings.BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_name = f"backup_{timestamp}.sql"
    dump_path = backup_dir / dump_name

    command = [
        settings.PG_DUMP_PATH,
        "-U",
        settings.POSTGRES_USER,
        "-h",
        settings.POSTGRES_HOST,
        "-p",
        str(settings.POSTGRES_PORT),
        "-d",
        settings.POSTGRES_DB,
        "-f",
        str(dump_path.resolve()),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Backup created: {dump_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {str(e)}")
    finally:
        os.environ.pop("PGPASSWORD", None)
