from enum import Enum


class MatchingStrategy(str, Enum):
    """Matching strategies"""

    EXTERNAL_ID = "external_id"
    MULTI_FIELD = "multi_field"
    MANUAL = "manual"


class TitleMatchCandidate:
    """A candidate title for matching"""

    def __init__(
        self,
        master_title_id: int,
        confidence: float,
        strategy: MatchingStrategy,
        details: dict | None = None,
    ):
        self.master_title_id = master_title_id
        self.confidence = confidence
        self.strategy = strategy
        self.details = details or {}

    def __repr__(self) -> str:
        return (
            f"TitleMatchCandidate(master_id={self.master_title_id}, "
            f"confidence={self.confidence:.2f}, strategy={self.strategy.value})"
        )
