from enum import Enum

__all__ = ["ConsolidationStatus"]


class ConsolidationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    CONSOLIDATED = "CONSOLIDATED"
    FAILED = "FAILED"
