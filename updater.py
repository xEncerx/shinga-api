import asyncio

from app.infrastructure.updater.global_titles_updater import GlobalTitlesUpdater
from app.core import *

async def main():
    async with GlobalTitlesUpdater(num_workers=7) as updater:
        await updater.idle()


if __name__ == "__main__":
    setup_logging("updater")

    asyncio.run(main())
