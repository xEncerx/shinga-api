from datetime import datetime
import pytest

from src.domain.services.title_merger import TitleMerger
from src.domain.models.titles import (
    TitleType,
    TitleStatus,
    TitleGenre,
    TitleData,
    TitleCategory,
    TitleCover,
)


class TestTitleMerger:
    @pytest.fixture
    def merger(self):
        return TitleMerger()

    @pytest.fixture
    def existing_title(self):
        return TitleData(
            name_ru="Атака титанов",
            name_en="Attack on Titan",
            description_ru="Существующее описание",
            description_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            popularity=100,
            chapters=139,
            views=1000000,
            volumes=34,
            favorites=50000,
            rating=9.0,
            scored_by=100000,
            released_at=datetime(2009, 9, 9),
            ended_at=None,
            genres=[TitleGenre.ACTION, TitleGenre.DRAMA],
            categories=[TitleCategory.MILITARY, TitleCategory.SURVIVAL],
            authors=["Hajime Isayama"],
            alt_names=["Shingeki no Kyojin", "進撃の巨人"],
            cover=TitleCover(original="https://example.com/existing_cover.jpg"),
        )

    @pytest.fixture
    def new_title(self):
        return TitleData(
            name_ru=None,
            name_en="Attack on Titan",
            description_ru=None,
            description_en="New English description",
            type=TitleType.MANGA,
            status=TitleStatus.FINISHED,
            popularity=50,
            chapters=139,
            views=500000,
            volumes=34,
            favorites=30000,
            rating=8.8,
            scored_by=50000,
            released_at=None,
            ended_at=datetime(2021, 4, 9),
            genres=[TitleGenre.ACTION, TitleGenre.FANTASY],
            categories=[TitleCategory.SURVIVAL, TitleCategory.MONSTERS],
            authors=["Isayama Hajime"],
            alt_names=["AoT", "Shingeki no Kyojin"],
            cover=TitleCover(thumbnail="http://example.com/cover.jpg"),
        )

    def test_merge_preserves_existing_text_fields(
        self,
        merger,
        existing_title,
        new_title,
    ):
        """Test: text fields are not overwritten if already filled"""
        result = merger.merge(existing_title, new_title)

        assert result.name_ru == "Атака титанов"
        assert result.name_en == "Attack on Titan"
        assert result.description_ru == "Существующее описание"
        assert result.description_en == "New English description"

    def test_merge_fills_empty_text_fields(self, merger, existing_title, new_title):
        """Test: empty text fields are filled from new title"""
        existing_title.description_en = None
        result = merger.merge(existing_title, new_title)

        assert result.description_en == "New English description"

    def test_merge_preserves_existing_type(self, merger, existing_title, new_title):
        """Test: title type does not change"""
        new_title.type = TitleType.MANHWA
        result = merger.merge(existing_title, new_title)

        assert result.type == TitleType.MANGA

    def test_merge_updates_status(self, merger, existing_title, new_title):
        """Test: status is updated from new title"""
        result = merger.merge(existing_title, new_title)

        assert result.status == TitleStatus.FINISHED

    def test_merge_takes_max_numeric_values(self, merger, existing_title, new_title):
        """Test: numeric fields take maximum value"""
        result = merger.merge(existing_title, new_title)

        assert result.popularity == 100  # max(100, 50)
        assert result.chapters == 139  # max(139, 139)
        assert result.views == 1000000  # max(1000000, 500000)
        assert result.volumes == 34  # max(34, 34)
        assert result.favorites == 50000  # max(50000, 30000)

    def test_merge_calculates_weighted_rating(self, merger, existing_title, new_title):
        """Test: rating is calculated as weighted average"""
        result = merger.merge(existing_title, new_title)

        # (9.0 * 100000 + 8.8 * 50000) / 150000 = 8.93
        expected_rating = 8.93
        assert result.rating == pytest.approx(expected_rating, rel=0.01)
        assert result.scored_by == 150000

    def test_merge_weighted_rating_with_zero_scores(self, merger):
        """Test: weighted average rating with zero scores"""
        title1 = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            rating=0.0,
            scored_by=0,
        )
        title2 = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            rating=0.0,
            scored_by=0,
        )

        result = merger.merge(title1, title2)
        assert result.rating == 0.0
        assert result.scored_by == 0

    def test_merge_dates(self, merger, existing_title, new_title):
        """Test: dates are filled when available"""
        result = merger.merge(existing_title, new_title)

        assert result.released_at == datetime(2009, 9, 9)
        assert result.ended_at == datetime(2021, 4, 9)

    def test_merge_genres(self, merger, existing_title, new_title):
        """Test: genres are merged without duplicates"""
        result = merger.merge(existing_title, new_title)

        # ACTION is present in both, should be without duplication
        expected_genres = {
            TitleGenre.ACTION,
            TitleGenre.DRAMA,
            TitleGenre.FANTASY,
        }
        assert set(result.genres) == expected_genres

    def test_merge_categories(self, merger, existing_title, new_title):
        """Test: categories are merged without duplicates"""
        result = merger.merge(existing_title, new_title)

        # SURVIVAL is present in both
        expected_categories = {
            TitleCategory.MILITARY,
            TitleCategory.SURVIVAL,
            TitleCategory.MONSTERS,
        }
        assert set(result.categories) == expected_categories

    def test_merge_authors_with_fuzzy_matching(self, merger, existing_title, new_title):
        """Test: authors are merged with removal of similar names via fuzzywuzzy"""
        result = merger.merge(existing_title, new_title)

        # "Hajime Isayama" and "Isayama Hajime" should be considered similar
        # Only one variant should remain
        assert len(result.authors) == 1
        assert "Hajime Isayama" in result.authors

    def test_merge_authors_with_different_names(self, merger, existing_title):
        """Test: different authors are added"""
        new_title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            authors=["Different Author"],
        )

        result = merger.merge(existing_title, new_title)

        assert len(result.authors) == 2
        assert "Hajime Isayama" in result.authors
        assert "Different Author" in result.authors

    def test_merge_alt_names_with_fuzzy_matching(
        self, merger, existing_title, new_title
    ):
        """Test: alternative names are merged with removal of duplicates"""
        result = merger.merge(existing_title, new_title)

        # "Shingeki no Kyojin" is present in both - should be without duplicates
        assert result.alt_names.count("Shingeki no Kyojin") == 1
        assert "進撃の巨人" in result.alt_names
        assert "AoT" in result.alt_names

    def test_merge_preserves_cover_url(self, merger, existing_title, new_title):
        """Test: cover URL does not change"""
        result = merger.merge(existing_title, new_title)

        assert result.cover.thumbnail == None

    def test_merge_empty_lists(self, merger):
        """Test: merging empty lists"""
        title1 = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[],
            categories=[],
            authors=[],
            alt_names=[],
        )
        title2 = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[TitleGenre.ACTION],
            categories=[TitleCategory.SURVIVAL],
            authors=["Author"],
            alt_names=["Alt Name"],
        )

        result = merger.merge(title1, title2)

        assert result.genres == [TitleGenre.ACTION]
        assert result.categories == [TitleCategory.SURVIVAL]
        assert result.authors == ["Author"]
        assert result.alt_names == ["Alt Name"]
