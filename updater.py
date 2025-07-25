from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
import asyncio

from app.infrastructure.updater import GlobalTitlesUpdater
from app.core import *

async def main():
    """
    Main function to run the GlobalFullParser.
    
    This implementation performs full parsing of data from supported providers:
    - MAL (MyAnimeList)
    - Remanga
    
    The process works as follows:
    1. Check which pages were parsed within the last 3 days
    2. Create queues with remaining pages that need to be parsed
    3. Start workers that process pages and update/create titles in the database
    3.1. For existing titles: update data
    3.2. For new titles: download covers and create database entries
    
    The system automatically calculates optimal number of workers based on available proxies.
    """
    try:
        async with GlobalTitlesUpdater() as updater:
            await updater.start_parsing()
    except KeyboardInterrupt:
        logger.info("Parsing interrupted by user")
    except Exception as e:
        logger.error(f"Error in full parsing: {e}")


if __name__ == "__main__":
    setup_logging("updater")

    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    asyncio.run(main())
