from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import TypeDecorator
from pydantic import BaseModel
from typing import Any
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class JSONBWithModel(TypeDecorator):
    """
    Custom SQLAlchemy type for storing Pydantic models as JSONB in PostgreSQL.

    Automatically converts:
    - Pydantic model → dict (when saving to DB)
    - dict → Pydantic model (when reading from DB)

    Supports both single models and lists of models.
    """

    impl = JSONB
    cache_ok = True

    def __init__(self, model_class: type[BaseModel]):
        """
        Initialize with a Pydantic model class.

        Args:
            model_class: Pydantic BaseModel class to use for conversion
        """
        self.model_class = model_class
        super().__init__()

    def process_bind_param(self, value: Any, dialect) -> Any:
        """
        Convert Python value to database value (dict/list).

        Called when saving data TO the database.

        Args:
            value: Python value (Pydantic model, dict, or list)
            dialect: Database dialect

        Returns:
            dict or list[dict] ready for JSONB storage
        """
        if value is None:
            return None

        if isinstance(value, self.model_class):
            return value.model_dump(mode="json", by_alias=True, exclude_none=False)

        elif isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, self.model_class):
                    result.append(
                        item.model_dump(mode="json", by_alias=True, exclude_none=False)
                    )
                elif isinstance(item, dict):
                    result.append(item)
                else:
                    result.append(item)
            return result

        elif isinstance(value, dict):
            return value

        elif isinstance(value, BaseModel):
            return value.model_dump(mode="json", by_alias=True, exclude_none=False)

        return value

    def process_result_value(self, value: Any, dialect) -> Any:
        """
        Convert database value (dict/list) to Python value (Pydantic model).

        Called when reading data FROM the database.

        Args:
            value: Database value (dict or list[dict])
            dialect: Database dialect

        Returns:
            Pydantic model instance or list of instances
        """
        if value is None:
            return None

        try:
            if isinstance(value, list):
                return [
                    self.model_class(**item) if isinstance(item, dict) else item
                    for item in value
                ]

            elif isinstance(value, dict):
                return self.model_class(**value)

            elif isinstance(value, self.model_class):
                return value

            return value

        except Exception as e:
            logger.error(
                f"Failed to deserialize {self.model_class.__name__} from {value}: {e}"
            )
            return value
