from src.presentation.api.schemas.errors import BaseAPIException, InternalServerError
from src.domain.errors.base import DomainError
from src.core import logger

from functools import wraps
from typing import Type, Callable


__all__ = ["map_domain_errors"]


def map_domain_errors(
    error_map: dict[Type[DomainError], Type[BaseAPIException]],
):
    """
    A decorator to map domain errors to API errors.

    Example:
    ```
    @map_domain_errors(
        {
            domain_errors.ValidationError: api_errors.ValidationError,
            domain_errors.UserAlreadyExistsError: api_errors.UserAlreadyExists,
        }
    )
    async def some_endpoint(...):
        ...
    ```
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except tuple(error_map.keys()) as e:
                api_error_class = error_map[type(e)]
                raise api_error_class(details=e.details)
            except Exception as e:
                logger.error(f"Unmapped domain error: {e}")
                raise InternalServerError()

        return wrapper

    return decorator
