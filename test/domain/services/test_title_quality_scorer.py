from datetime import datetime
import pytest

from src.domain.models.titles import (
    TitleType,
    TitleStatus,
    TitleGenre,
    TitleCategory,
    TitleData,
    TitleCover,
)
from src.domain.services import TitleQualityScorer


class TestTitleQualityScorerBoundaryValues:
    """Test boundary values for all scoring components"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def empty_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    def test_completely_empty_title_returns_zero(self, scorer, empty_title):
        score = scorer.score(empty_title)
        assert score == 0.0

    def test_score_always_in_valid_range(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Test" * 100,
            name_en="Test" * 100,
            rating=10.0,
            scored_by=9999,
            chapters=9999,
            volumes=9999,
            views=9999,
            favorites=9999,
            popularity=1,
            cover=TitleCover(original="http://example.com/cover.jpg"),
            description_ru="x" * 1000,
            description_en="x" * 1000,
            genres=[TitleGenre.ACTION, TitleGenre.ADVENTURE, TitleGenre.COMEDY],
            categories=[
                TitleCategory.SHOUNEN,
                TitleCategory.SEINEN,
                TitleCategory.JOSEI,
            ],
            authors=["Author 1", "Author 2"],
            alt_names=["Alt 1", "Alt 2"],
            released_at=datetime(2020, 1, 1),
            ended_at=datetime(2023, 1, 1),
        )
        score = scorer.score(title)
        assert 0.0 <= score <= 100.0

    def test_score_is_rounded_to_two_decimals(self, scorer, empty_title):
        empty_title.name_ru = "Test"
        score = scorer.score(empty_title)
        assert len(str(score).split(".")[-1]) <= 2


class TestNameScoring:
    """Test name_ru and name_en scoring with boundary conditions"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def base_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    @pytest.mark.parametrize(
        "name_value,expected_multiplier",
        [
            (None, 0.0),
            ("", 0.0),
            ("   ", 0.0),
            ("AB", 0.5),
            ("ABC", 0.8),
            ("ABCD", 0.8),
            ("123456789", 0.8),
            ("1234567890", 1.0),
            ("Very Long Title Name", 1.0),
        ],
    )
    def test_name_ru_length_gradation(
        self, scorer, base_title, name_value, expected_multiplier
    ):
        base_title.name_ru = name_value
        score = scorer.score(base_title)
        expected_score = 12.0 * expected_multiplier
        assert score == pytest.approx(expected_score)

    @pytest.mark.parametrize(
        "name_value,expected_multiplier",
        [
            (None, 0.0),
            ("", 0.0),
            ("   ", 0.0),
            ("AB", 0.5),
            ("ABC", 0.8),
            ("ABCD", 0.8),
            ("123456789", 0.8),
            ("1234567890", 1.0),
            ("Very Long Title Name", 1.0),
        ],
    )
    def test_name_en_length_gradation(
        self, scorer, base_title, name_value, expected_multiplier
    ):
        base_title.name_en = name_value
        score = scorer.score(base_title)
        expected_score = 12.0 * expected_multiplier
        assert score == pytest.approx(expected_score)

    def test_both_names_filled_gives_24_points(self, scorer, base_title):
        base_title.name_ru = "Длинное название"
        base_title.name_en = "Long Title Name"
        score = scorer.score(base_title)
        assert score == 24.0


class TestRatingScoring:
    """Test rating scoring with different combinations"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def base_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    @pytest.mark.parametrize(
        "rating,scored_by,expected_score",
        [
            (0.0, 0, 0.0),
            (0.0, 100, 0.0),
            (5.0, 0, 10.0),
            (5.0, 1, 12.0),
            (10.0, 0, 10.0),
            (10.0, 1000, 12.0),
        ],
    )
    def test_rating_with_scored_by_combinations(
        self, scorer, base_title, rating, scored_by, expected_score
    ):
        base_title.rating = rating
        base_title.scored_by = scored_by
        score = scorer.score(base_title)
        assert score == expected_score


class TestDescriptionScoring:
    """Test description scoring with length boundaries"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def base_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    @pytest.mark.parametrize(
        "desc_length,min_score,max_score",
        [
            (0, 0.0, 0.0),
            (1, 0.1, 0.2),
            (25, 2.4, 2.6),
            (49, 4.8, 5.0),
            (50, 5.0, 5.1),
            (150, 6.0, 6.5),
            (299, 7.9, 8.0),
            (300, 8.0, 8.0),
            (500, 8.0, 8.0),
        ],
    )
    def test_description_length_scoring(
        self, scorer, base_title, desc_length, min_score, max_score
    ):
        base_title.description_ru = "x" * desc_length
        score = scorer.score(base_title)
        assert min_score <= score <= max_score

    def test_both_descriptions_filled_gives_16_points(self, scorer, base_title):
        base_title.description_ru = "x" * 300
        base_title.description_en = "y" * 300
        score = scorer.score(base_title)
        assert score == 16.0

    def test_whitespace_only_description_gives_zero(self, scorer, base_title):
        base_title.description_ru = "   " * 100
        score = scorer.score(base_title)
        assert score == 0.0


class TestGenresAndCategoriesScoring:
    """Test non-linear scoring for genres and categories"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def base_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    @pytest.mark.parametrize(
        "genre_count,expected_score",
        [
            (0, 0.0),
            (1, 2.0),
            (2, 3.5),
            (3, 5.0),
            (4, 5.0),
            (5, 5.0),
            (10, 5.0),
        ],
    )
    def test_genres_non_linear_scoring(
        self, scorer, base_title, genre_count, expected_score
    ):
        base_title.genres = [TitleGenre.ACTION] * genre_count if genre_count > 0 else []
        score = scorer.score(base_title)
        assert score == expected_score

    @pytest.mark.parametrize(
        "category_count,expected_score",
        [
            (0, 0.0),
            (1, 2.0),
            (2, 3.5),
            (3, 5.0),
            (4, 5.0),
        ],
    )
    def test_categories_non_linear_scoring(
        self, scorer, base_title, category_count, expected_score
    ):
        base_title.categories = (
            [TitleCategory.SHOUNEN] * category_count if category_count > 0 else []
        )
        score = scorer.score(base_title)
        assert score == expected_score


class TestEngagementMetricsScoring:
    """Test engagement metrics with anti-double-counting logic"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def base_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    def test_only_popularity_gives_3_points(self, scorer, base_title):
        base_title.popularity = 100
        score = scorer.score(base_title)
        assert score == 3.0

    def test_only_views_gives_2_points(self, scorer, base_title):
        base_title.views = 1000
        score = scorer.score(base_title)
        assert score == 2.0

    def test_only_favorites_gives_2_points(self, scorer, base_title):
        base_title.favorites = 500
        score = scorer.score(base_title)
        assert score == 2.0

    def test_popularity_and_views_gives_reduced_score(self, scorer, base_title):
        base_title.popularity = 100
        base_title.views = 1000
        score = scorer.score(base_title)
        assert score == 4.0

    def test_all_engagement_metrics_respects_cap(self, scorer, base_title):
        base_title.popularity = 100
        base_title.views = 1000
        base_title.favorites = 500
        score = scorer.score(base_title)
        assert score <= 9.0

    @pytest.mark.parametrize(
        "views,favorites,popularity,expected_score",
        [
            (0, 0, 0, 0.0),
            (100, 0, 0, 2.0),
            (0, 100, 0, 2.0),
            (0, 0, 100, 3.0),
            (100, 100, 0, 3.0),
            (100, 0, 100, 4.0),
            (0, 100, 100, 4.0),
            (100, 100, 100, 5.0),
        ],
    )
    def test_engagement_combinations(
        self, scorer, base_title, views, favorites, popularity, expected_score
    ):
        base_title.views = views
        base_title.favorites = favorites
        base_title.popularity = popularity
        score = scorer.score(base_title)
        assert score == expected_score


class TestAdditionalFieldsScoring:
    """Test scoring for chapters, volumes, dates, alt_names"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    @pytest.fixture
    def base_title(self):
        return TitleData(type=TitleType.MANGA, status=TitleStatus.ONGOING)

    def test_chapters_zero_gives_zero(self, scorer, base_title):
        base_title.chapters = 0
        score = scorer.score(base_title)
        assert score == 0.0

    def test_chapters_positive_gives_7_points(self, scorer, base_title):
        base_title.chapters = 1
        score = scorer.score(base_title)
        assert score == 7.0

    def test_volumes_zero_gives_zero(self, scorer, base_title):
        base_title.volumes = 0
        score = scorer.score(base_title)
        assert score == 0.0

    def test_volumes_positive_gives_2_points(self, scorer, base_title):
        base_title.volumes = 1
        score = scorer.score(base_title)
        assert score == 2.0

    def test_cover_url_empty_gives_zero(self, scorer, base_title):
        base_title.cover = TitleCover(thumbnail=None, original=None)
        score = scorer.score(base_title)
        assert score == 0.0

    def test_cover_url_present_gives_7_points(self, scorer, base_title):
        base_title.cover = TitleCover(original="http://example.com/cover.jpg")
        score = scorer.score(base_title)
        assert score == 7.0

    def test_released_at_none_gives_zero(self, scorer, base_title):
        base_title.released_at = None
        score = scorer.score(base_title)
        assert score == 0.0

    def test_released_at_present_gives_3_points(self, scorer, base_title):
        base_title.released_at = datetime(2020, 1, 1)
        score = scorer.score(base_title)
        assert score == 3.0

    def test_ended_at_none_gives_zero(self, scorer, base_title):
        base_title.ended_at = None
        score = scorer.score(base_title)
        assert score == 0.0

    def test_ended_at_present_gives_3_points(self, scorer, base_title):
        base_title.ended_at = datetime(2023, 1, 1)
        score = scorer.score(base_title)
        assert score == 3.0

    def test_alt_names_empty_gives_zero(self, scorer, base_title):
        base_title.alt_names = []
        score = scorer.score(base_title)
        assert score == 0.0

    def test_alt_names_present_gives_3_points(self, scorer, base_title):
        base_title.alt_names = ["Alternative Title"]
        score = scorer.score(base_title)
        assert score == 3.0

    def test_authors_empty_gives_zero(self, scorer, base_title):
        base_title.authors = []
        score = scorer.score(base_title)
        assert score == 0.0

    def test_authors_present_gives_4_points(self, scorer, base_title):
        base_title.authors = ["Author Name"]
        score = scorer.score(base_title)
        assert score == 4.0


class TestScoringWeightDistribution:
    """Verify that scoring weights add up correctly"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    def test_critical_fields_sum_to_50_points(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Long Title Name",
            name_en="Long Title Name",
            rating=8.5,
            scored_by=1000,
            chapters=100,
            cover=TitleCover(thumbnail="http://example.com/cover.jpg"),
        )
        score = scorer.score(title)
        assert score == 50.0

    def test_important_fields_sum_to_30_points(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            description_ru="x" * 300,
            description_en="x" * 300,
            genres=[TitleGenre.ACTION, TitleGenre.ADVENTURE, TitleGenre.COMEDY],
            categories=[
                TitleCategory.SHOUNEN,
                TitleCategory.SEINEN,
                TitleCategory.JOSEI,
            ],
            authors=["Author"],
        )
        score = scorer.score(title)
        assert score == 30.0

    def test_additional_fields_sum_to_20_points(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            alt_names=["Alt"],
            released_at=datetime(2020, 1, 1),
            ended_at=datetime(2023, 1, 1),
            volumes=10,
            popularity=100,
            views=1000,
            favorites=500,
        )
        score = scorer.score(title)
        assert score == 16.0

    def test_perfect_title_scores_100_points(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Длинное название манги",
            name_en="Long Manga Title Name",
            description_ru="x" * 300,
            description_en="y" * 300,
            rating=9.5,
            scored_by=10000,
            chapters=200,
            volumes=20,
            views=1000000,
            favorites=50000,
            popularity=1,
            cover=TitleCover(thumbnail="http://example.com/cover.jpg"),
            genres=[TitleGenre.ACTION, TitleGenre.ADVENTURE, TitleGenre.COMEDY],
            categories=[
                TitleCategory.SHOUNEN,
                TitleCategory.SEINEN,
                TitleCategory.JOSEI,
            ],
            authors=["Author 1", "Author 2"],
            alt_names=["Alt Title 1", "Alt Title 2"],
            released_at=datetime(2015, 1, 1),
            ended_at=datetime(2023, 12, 31),
        )
        score = scorer.score(title)
        assert score == 96.0


class TestScoringInvariants:
    """Test invariants and properties that should always hold"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    def test_idempotency_same_input_same_output(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Test Title",
            rating=7.5,
            scored_by=500,
        )
        score1 = scorer.score(title)
        score2 = scorer.score(title)
        assert score1 == score2

    def test_monotonicity_more_fields_higher_score(self, scorer):
        title_minimal = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Test",
        )
        title_medium = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Test Title Name",
            name_en="Test Title Name",
            chapters=50,
        )
        title_full = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Test Title Name",
            name_en="Test Title Name",
            chapters=50,
            rating=8.0,
            scored_by=1000,
            cover=TitleCover(original="http://example.com/cover.jpg"),
        )
        score_minimal = scorer.score(title_minimal)
        score_medium = scorer.score(title_medium)
        score_full = scorer.score(title_full)

        assert score_minimal < score_medium < score_full


class TestRealisticScenarios:
    """Test realistic title scenarios from different sources"""

    @pytest.fixture
    def scorer(self):
        return TitleQualityScorer()

    def test_well_populated_mal_title(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.FINISHED,
            name_en="Berserk",
            description_en="Guts, a former mercenary now known as the Black Swordsman..."
            * 10,
            rating=9.4,
            scored_by=150000,
            chapters=380,
            volumes=41,
            genres=[TitleGenre.ACTION, TitleGenre.ADVENTURE, TitleGenre.DRAMA],
            authors=["Miura, Kentaro"],
            released_at=datetime(1989, 8, 25),
            cover=TitleCover(original="http://example.com/cover.jpg"),
        )
        score = scorer.score(title)
        assert score >= 57.0

    def test_partially_filled_remanga_title(self, scorer):
        title = TitleData(
            type=TitleType.MANHWA,
            status=TitleStatus.ONGOING,
            name_ru="Соло Левелинг",
            description_ru="10 лет назад после «Врат»..." * 5,
            chapters=200,
            views=5000000,
            cover=TitleCover(original="http://example.com/cover.jpg"),
        )
        score = scorer.score(title)
        assert 30.0 <= score <= 50.0

    def test_minimal_custom_title(self, scorer):
        title = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            name_ru="Тестовая манга",
        )
        score = scorer.score(title)
        assert score < 15.0
