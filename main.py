import asyncio

from app.infrastructure.managers import QueueManager, ProxyManager
from app.infrastructure.storage import CoverManger
from app.providers import MalProvider
from app.providers.mal.parser import MalParser
from app.core import *


async def main():
    # queue_manager = QueueManager(num_workers=10)
    # await queue_manager.initialize()
    # await queue_manager.run()
    manager = ProxyManager()
    await manager.initialize()
    await manager.cleanup()


if __name__ == "__main__":
    setup_logging()

    asyncio.run(main())
