from src.domain.models import EnvFlavor

from loguru import logger
import logging
import sys

__all__ = ["setup_logger", "logger"]


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def setup_fastapi_logging() -> None:
    # Intercept all uvicorn-related loggers including new ones
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "fastapi",
    ]
    for log_name in uvicorn_loggers:
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False


def setup_taskiq_logging() -> None:
    remove_taskiq_loggers = ["taskiq.receiver.receiver"]
    for log_name in remove_taskiq_loggers:
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = []
        logging_logger.propagate = False


def setup_logger(flavor: EnvFlavor, level: str = "INFO") -> None:
    """Sets up the logging configuration for the application."""
    logger.remove()  # Remove default logger

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        # "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        level=level,
        format=log_format,
        colorize=False if flavor == EnvFlavor.PRODUCTION else True,
        backtrace=True,
        diagnose=True,
        # serialize=True if flavor == EnvFlavor.PRODUCTION else False,
    )

    setup_fastapi_logging()
    setup_taskiq_logging()

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
