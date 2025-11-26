from loguru import logger
import sys

import logging


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_standard_logging() -> None:
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    uvicorn_loggers = ["uvicorn", "uvicorn.error", "uvicorn.access"]
    for log_name in uvicorn_loggers:
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    celery_loggers = ["celery", "celery.worker", "celery.task", "celery.app"]
    for log_name in celery_loggers:
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = []
        logging_logger.setLevel(logging.ERROR)
        logging_logger.propagate = False


def setup_logging(file_name: str = "") -> None:
    """
    Sets up the logging configuration for the application.

    Args:
        file_name (str): The name of the log file(without .log). If empty, logs will save in .log file.
    """
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:DD:MM:YYYY HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    logger.add(
        f"logs/{file_name}.log",
        rotation="50 MB",
        retention="30 days",
        compression=None,
        level="INFO",
        format="{time:DD:MM:YYYY HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        delay=True,
    )

    configure_standard_logging()
