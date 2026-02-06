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
    uvicorn_loggers = ["uvicorn", "uvicorn.error", "uvicorn.access"]
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

    logger.add(
        sys.stderr,
        level=level,
        colorize=False if flavor == EnvFlavor.PRODUCTION else True,
        backtrace=True,
        diagnose=True,
        serialize=True if flavor == EnvFlavor.PRODUCTION else False,
    )

    setup_fastapi_logging()
    setup_taskiq_logging()

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
