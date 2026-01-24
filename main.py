from src.application.tasks import *
from src.infrastructure.tasks import *

from src.domain.models.source import Source

import asyncio

# ! Just test file, will be deleted later


async def main():
    await broker.startup()

    task = await enqueue_consolidation_jobs_task.kiq()  # type: ignore
    task = await parse_source_page_task.kiq(
        Source.REMANGA,
        2,
        10,
    )  # type: ignore
    result = await task.wait_result(timeout=15)
    print(f"Task execution took: {result.execution_time} seconds.")
    print(result.return_value)

    await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
