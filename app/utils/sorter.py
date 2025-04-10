from difflib import SequenceMatcher
from typing import Any
from enum import Enum

from app.models import MangaBase


class SorterEnum(str, Enum):
    BY_NAME = "name"
    BY_DATE = "date"
    BY_RATING = "rating"
    BY_CHAPTERS = "chapters"
    BY_STATUS = "status"  # TODO: Implement status sorting


class MangaSorter:
    def sort(
        self,
        manga_list: list[MangaBase],
        by: SorterEnum,
        extra_data: Any = None,
        reverse: bool = False,
    ) -> list[MangaBase]:
        """
        Sorts the given manga list based on the specified sorting method.
        Args:
                manga_list (list[MangaBase]): List of manga objects to be sorted.
                by (SorterEnum): Enum value specifying the sorting method to use.
                extra_data (Any, optional): Additional data required for sorting.
                        For example, a search query when sorting by name. Defaults to None.
                reverse (bool, optional): If True, reverses the order of the sorted list. Defaults to False.
        Returns:
                list[MangaBase]: Sorted list of manga objects.
        Raises:
                ValueError: If an unknown sorting method is specified.
        Example:
                >>> sorter = Sorter()
                >>> sorted_manga = sorter.sort(manga_list, SorterEnum.BY_NAME, reverse=True)
        """

        result: list[MangaBase] = []

        match by:
            case SorterEnum.BY_NAME:
                result = self._sort_manga_by_name(
                    query=extra_data,
                    manga_list=manga_list,
                )
            case SorterEnum.BY_DATE:
                result = self._sort_manga_by_data(manga_list=manga_list)
            case SorterEnum.BY_RATING:
                result = self._sort_manga_by_rating(manga_list=manga_list)
            case SorterEnum.BY_CHAPTERS:
                result = self._sort_manga_by_chapters(manga_list=manga_list)
            # TODO: Implement status sorting
            case _:
                raise ValueError(f"Unknown sorting method: {by}")

        if reverse and len(result) > 0:
            result.reverse()

        return result

    @staticmethod
    def _sort_manga_by_data(manga_list: list[MangaBase]) -> list[MangaBase]:
        return sorted(manga_list, key=lambda x: x.last_read, reverse=True)

    @staticmethod
    def _sort_manga_by_rating(manga_list: list[MangaBase]) -> list[MangaBase]:
        return sorted(manga_list, key=lambda x: x.avg_rating, reverse=True)

    @staticmethod
    def _sort_manga_by_chapters(manga_list: list[MangaBase]) -> list[MangaBase]:
        return sorted(manga_list, key=lambda x: x.chapters, reverse=True)

    @staticmethod
    def _sort_manga_by_name(query: str, manga_list: list[MangaBase]) -> list[MangaBase]:
        if not query:
            return manga_list

        query = query.lower().strip()

        def calculate_similarity(target: str, is_main_name: bool = False) -> float:
            target = target.lower().strip()
            base_score = SequenceMatcher(None, query, target).ratio()

            contains_bonus = 0.3 if query in target else 0
            start_bonus = 0.2 if target.startswith(query) else 0

            main_name_bonus = 0.1 if is_main_name else 0

            return min(base_score + contains_bonus + start_bonus + main_name_bonus, 1.0)

        def get_manga_score(manga: MangaBase) -> float:
            scores = [calculate_similarity(manga.name, is_main_name=True)]

            if manga.alt_names:
                alt_scores = [
                    calculate_similarity(alt_name)
                    for alt_name in manga.alt_names.split("/")
                    if alt_name.strip()
                ]
                scores.extend(alt_scores)

            return max(scores)

        return sorted(manga_list, key=get_manga_score, reverse=True)


manga_sorter = MangaSorter()
