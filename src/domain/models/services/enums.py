from enum import Enum

__all__ = ["ConsolidationStatus"]


class ConsolidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CONSOLIDATED = "consolidated"
    FAILED = "failed"
