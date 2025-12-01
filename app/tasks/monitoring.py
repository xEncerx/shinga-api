from datetime import datetime, timezone
from sqlmodel import select, func
from pprint import pformat

from app.infrastructure.db.models.title_source_data import TitleSourceData
from .event_loop_controller import execute_async_task
from app.infrastructure.db.session import get_session
from app.infrastructure.db.models.title import Title
from app.core.celery_config import celery_app
from app.domain.enums import SourceProvider
from app.core import logger, settings


@celery_app.task(name="app.tasks.monitoring.collect_statistics")
def collect_statistics() -> dict:
    """
    Collect system statistics.

    Collects:
    - Total number of titles
    - Number of sources
    - Number of mappings
    - Data quality
    - Provider statistics

    Returns:
        dict: Statistics dictionary.
    """
    try:
        logger.info("Collecting system statistics")

        async def run():
            async with get_session() as session:
                stats = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "titles": {},
                    "sources": {},
                }

                # === Titles statistics ===
                total_titles = await session.exec(select(func.count(Title.id)))  # type: ignore
                stats["titles"]["total"] = total_titles.one()

                # Average data quality
                avg_quality = await session.exec(
                    select(func.avg(Title.data_quality_score))
                )
                stats["titles"]["avg_quality_score"] = float(avg_quality.one() or 0.0)

                # Titles with covers
                titles_with_cover = await session.exec(
                    select(func.count(Title.id)).where(  # type: ignore
                        Title.cover.isnot(None),  # type: ignore
                        Title.cover["url"].astext.isnot(None),  # type: ignore
                        Title.cover["url"].astext != settings.COVER_404_PATH,  # type: ignore
                        Title.cover["url"].astext != settings.COVER_PENDING_PATH,  # type: ignore
                    )
                )
                stats["titles"]["with_cover"] = titles_with_cover.one()

                # === Sources statistics ===
                total_source_data = await session.exec(
                    select(func.count(TitleSourceData.id))  # type: ignore
                )
                stats["sources"]["total"] = total_source_data.one()

                # Unmapped sources
                unmapped_sources = await session.exec(
                    select(func.count(TitleSourceData.id)).where(  # type: ignore
                        TitleSourceData.master_title_id == None
                    )
                )
                stats["sources"]["unmapped"] = unmapped_sources.one()

                # Deleted sources
                deleted_sources = await session.exec(
                    select(func.count(TitleSourceData.id)).where(  # type: ignore
                        TitleSourceData.is_deleted_from_source == True
                    )
                )
                stats["sources"]["deleted"] = deleted_sources.one()

                # By providers
                for provider in SourceProvider:
                    provider_count = await session.exec(
                        select(func.count(TitleSourceData.id)).where(  # type: ignore
                            TitleSourceData.source_provider == provider
                        )
                    )
                    stats["sources"][provider.value] = provider_count.one()

                return stats

        result = execute_async_task(run())
        logger.info(pformat(result))

        return result

    except Exception as e:
        logger.error(f"Collect_statistics failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
