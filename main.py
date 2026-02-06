from src.application.tasks import *
from src.infrastructure.tasks import *

from src.domain.models.source import Source

from src.infrastructure.sources import MalClient, AniListClient
import time
from pprint import pprint

import asyncio

# ! Just test file, will be deleted later


async def main():
    await broker.startup()

    task = await enqueue_consolidation_jobs_task.kiq()  # type: ignore
    # task = await parse_source_page_task.kiq(
    #     Source.ANILIST,
    #     1,
    #     50,
    # )  # type: ignore
    result = await task.wait_result(timeout=15)
    print(f"Task execution took: {result.execution_time} seconds.")
    print(result.return_value)

    await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
