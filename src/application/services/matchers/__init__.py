from .mal_id_matcher import MalIdMatcher
from .title_name_matcher import TitleNameMatcher

AVAILABLE_MATCHERS = [MalIdMatcher, TitleNameMatcher]

__all__ = ["MalIdMatcher", "TitleNameMatcher", "AVAILABLE_MATCHERS"]
