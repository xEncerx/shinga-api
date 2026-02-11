from taskiq import TaskiqEvents, TaskiqState

from src.infrastructure.sources import SourceManager, AVAILABLE_SOURCES
from src.infrastructure.db.session import async_session, engine
from src.infrastructure.email import SMTPEmailService
from src.infrastructure.storage import LocalFileStorage
from src.infrastructure.network import MediaDownloader
from src.infrastructure.media import ImageProcessor
from src.core import settings, setup_logger
from src.application.use_cases import *
from .broker import broker


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    setup_logger(settings.FLAVOR)

    state.session_factory = async_session
    state.source_manager = SourceManager(
        providers=AVAILABLE_SOURCES, base_proxy=settings.PROXY
    )
    state.cover_storage = LocalFileStorage(
        base_path=settings.STORAGE_BASE_PATH + settings.COVER_STORAGE_FOLDER,
        public_url_prefix=settings.COVER_PUBLIC_URL,
    )
    state.media_downloader = MediaDownloader(
        timeout=15,
        proxy=settings.PROXY,
    )
    state.image_processor = ImageProcessor(
        quality=settings.IMAGE_QUALITY,
        output_format=settings.BASE_IMAGE_FORMAT,
    )
    state.email_service = SMTPEmailService(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD,
        email_domain=settings.EMAIL_DOMAIN,
        use_tls=settings.SMTP_USE_TLS,
    )

    await state.media_downloader.create_session()
    await state.source_manager.initialize()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    await state.media_downloader.close()
    await state.source_manager.dispose()
    await engine.dispose()
