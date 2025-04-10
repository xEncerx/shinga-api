from logging.handlers import RotatingFileHandler
from typing import Optional
from pathlib import Path
import logging

from app.core import settings


def setup_logger(
    name: str = "ShingaLogger",
    log_file: Optional[str] = "logs/server.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    if log_file:
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(levelname)s: \t  %(asctime)s | %(message)s", datefmt="%H:%M:%S %d-%m"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if log_file:
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    uvicorn_loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("uvicorn.access"),
    ]

    for ulogger in uvicorn_loggers:
        ulogger.handlers.clear()
        if log_file:
            ulogger.addHandler(file_handler)
        ulogger.addHandler(console_handler)
        ulogger.setLevel(level)
        ulogger.propagate = False

    return logger


logger = setup_logger(
    log_file=settings.LOG_PATH if settings.FILE_LOGGING else None,
    level=settings.LOG_LEVEL,
    max_bytes=settings.LOG_MAX_SIZE,
    backup_count=settings.LOG_BACKUP_COUNT,
)
