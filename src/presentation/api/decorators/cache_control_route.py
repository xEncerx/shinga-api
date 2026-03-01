from typing import Callable, Type

from fastapi import Request, Response
from fastapi.routing import APIRoute

__all__ = ["cache_control_route"]

ONE_WEEK = 60 * 60 * 24 * 7


def cache_control_route(max_age: int = ONE_WEEK) -> Type[APIRoute]:
    class CacheControlRoute(APIRoute):
        def get_route_handler(self) -> Callable:
            original_handler = super().get_route_handler()

            async def handler(request: Request) -> Response:
                response: Response = await original_handler(request)
                response.headers["Cache-Control"] = f"public, max-age={max_age}"
                return response

            return handler

    return CacheControlRoute