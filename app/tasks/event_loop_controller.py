import asyncio
import time
from threading import Thread
from typing import TypeVar, Awaitable


class _SingleEventLoop:
    _loop: asyncio.AbstractEventLoop | None = None
    _loop_thread: Thread | None = None

    def _ensure_loop_is_running(self):
        if self._loop and not self._loop.is_running():
            self._loop.close()
            self._loop = None

        if self._loop is None:
            self._loop_thread = Thread(target=self._eventloop_thread_run, daemon=True)
            self._loop_thread.start()
            time.sleep(0.1)

    def _eventloop_thread_run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def execute_async_task(self, coroutine):
        self._ensure_loop_is_running()
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)  # type: ignore
        return future.result()


_single_event_loop = _SingleEventLoop()

R = TypeVar("R")


def execute_async_task(coroutine: Awaitable[R]) -> R:
    """
    Execute an asynchronous task in a dedicated event loop running in a separate thread.

    Args:
        coroutine (Awaitable[R]): The coroutine to be executed.

    Returns:
        R: The result of the coroutine.
    """
    return _single_event_loop.execute_async_task(coroutine)
