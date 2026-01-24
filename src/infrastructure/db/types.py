from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import TypeDecorator
from pydantic import BaseModel
from typing import Type


class PydanticJsonType(TypeDecorator):
    """SQLAlchemy type for automatic serialization of Pydantic models to JSONB"""

    impl = JSONB
    cache_ok = True

    def __init__(self, pydantic_model: Type[BaseModel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pydantic_model = pydantic_model

    def process_bind_param(
        self, value: BaseModel | dict | None, dialect
    ) -> dict | None:
        """Convert Python -> Database"""
        if value is None:
            return None

        if isinstance(value, dict):
            return value

        if isinstance(value, self.pydantic_model):
            return value.model_dump(mode="json")

        return value  # type: ignore

    def process_result_value(self, value: dict | None, dialect) -> BaseModel | None:
        """Convert Database -> Python"""
        if value is None or not value:
            return None

        if isinstance(value, dict):
            return self.pydantic_model.model_validate(value)

        return value
