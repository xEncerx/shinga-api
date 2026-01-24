from datetime import datetime, timedelta
import pytest

from src.domain.models.titles import (
    TitleType,
    TitleStatus,
    TitleGenre,
    TitleCategory,
    TitleData,
)
from src.domain.services import TitleSimilarityScorer


@pytest.fixture
def scorer():
    return TitleSimilarityScorer()


@pytest.fixture
def base_title():
    return TitleData(
        name_ru="Берсерк",
        name_en="Berserk",
        description_ru="Темное фэнтези о мечнике Гатсе",
        description_en="Dark fantasy about swordsman Guts",
        type=TitleType.MANGA,
        status=TitleStatus.ONGOING,
        chapters=374,
        volumes=41,
        released_at=datetime(1989, 8, 25),
        ended_at=None,
        genres=[TitleGenre.ACTION, TitleGenre.FANTASY, TitleGenre.HORROR],
        categories=[TitleCategory.SHOUNEN],
        authors=["Kentaro Miura"],
        alt_names=["ベルセルク", "Berserk: The Prototype"],
        rating=9.4,
        scored_by=150000,
    )


class TestBlockingField:
    """Test type blocking field - different types should return 0.0"""

    @pytest.mark.parametrize(
        "type_a,type_b",
        [
            (TitleType.MANGA, TitleType.MANHWA),
            (TitleType.MANGA, TitleType.MANHUA),
            (TitleType.MANGA, TitleType.NOVEL),
            (TitleType.MANHWA, TitleType.MANHUA),
        ],
    )
    def test_different_types_return_zero(self, scorer, base_title, type_a, type_b):
        title_a = base_title.model_copy(update={"type": type_a})
        title_b = base_title.model_copy(update={"type": type_b})

        score = scorer.score(title_a, title_b)

        assert score == 0.0

    def test_same_type_returns_nonzero(self, scorer, base_title):
        title_a = base_title.model_copy()
        title_b = base_title.model_copy()

        score = scorer.score(title_a, title_b)

        assert score > 0.0


class TestNameMatching:
    """Test name similarity scoring (45% weight)"""

    def test_identical_names_high_score(self, scorer, base_title):
        title_a = base_title.model_copy()
        title_b = base_title.model_copy()

        score = scorer.score(title_a, title_b)

        assert score >= 95.0

    def test_cyrillic_latin_transliteration(self, scorer):
        title_a = TitleData(
            name_ru="Берсерк",
            name_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_ru=None,
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score > 80.0

    def test_completely_different_names(self, scorer):
        title_a = TitleData(
            name_en="Attack on Titan",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="One Piece",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score < 50.0

    def test_empty_names_both_titles(self, scorer):
        title_a = TitleData(
            name_ru=None,
            name_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_ru=None,
            name_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score == 0.0

    def test_one_title_has_names_other_empty(self, scorer):
        title_a = TitleData(
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_ru=None,
            name_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score == 0.0

    def test_alt_names_matching(self, scorer):
        title_a = TitleData(
            name_en="Attack on Titan",
            alt_names=["Shingeki no Kyojin", "進撃の巨人"],
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="Shingeki no Kyojin",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score >= 85.0

    def test_duplicate_names_deduplication(self, scorer):
        title_a = TitleData(
            name_en="Berserk",
            alt_names=["Berserk", "BERSERK", "berserk"],
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score >= 85.0

    def test_names_with_special_characters(self, scorer):
        title_a = TitleData(
            name_en="Re:Zero - Starting Life in Another World",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="ReZero Starting Life in Another World",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score >= 85.0


class TestDescriptionMatching:
    """Test description similarity scoring (7% weight)"""

    def test_identical_descriptions(self, scorer, base_title):
        title_a = base_title.model_copy()
        title_b = base_title.model_copy()

        score = scorer.score(title_a, title_b)

        assert score >= 95.0

    def test_empty_descriptions_both_titles(self, scorer):
        title_a = TitleData(
            name_en="Test",
            description_ru=None,
            description_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="Test",
            description_ru=None,
            description_en=None,
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert score > 0.0

    def test_partial_description_overlap(self, scorer):
        title_a = TitleData(
            name_en="Test",
            description_en="A story about a young hero fighting evil monsters in a fantasy world",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="Test",
            description_en="Fighting evil monsters in a fantasy world with magic and swords",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert 70.0 < score < 100.0


class TestTypeAndStatus:
    """Test type and status matching (15% weight)"""

    def test_same_type_same_status(self, scorer, base_title):
        title_a = base_title.model_copy()
        title_b = base_title.model_copy()

        score = scorer.score(title_a, title_b)

        assert score >= 95.0

    def test_same_type_different_status(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.FINISHED,
        )

        score = scorer.score(title_a, title_b)

        assert score > 70.0


class TestDateMatching:
    """Test date similarity with tolerance (15% weight)"""

    @pytest.mark.parametrize(
        "days_diff,expected_min",
        [
            (0, 0.99),
            (1, 0.99),
            (30, 0.90),
            (182, 0.50),
            (365, 0.01),
        ],
    )
    def test_released_at_tolerance(self, scorer, days_diff, expected_min):
        base_date = datetime(2000, 1, 1)
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=base_date,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=base_date + timedelta(days=days_diff),
        )

        score = scorer.score(title_a, title_b)

        assert score >= expected_min

    def test_dates_beyond_tolerance(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=datetime(2000, 1, 1),
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=datetime(2002, 1, 1),
        )

        score = scorer.score(title_a, title_b)

        assert score < 95.0

    def test_one_date_none(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=datetime(2000, 1, 1),
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=None,
        )

        score = scorer.score(title_a, title_b)

        assert score > 0.0

    def test_both_dates_none(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=None,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            released_at=None,
        )

        score = scorer.score(title_a, title_b)

        assert score > 0.0


class TestNumericFields:
    """Test chapters and volumes similarity with tolerance (8% weight)"""

    @pytest.mark.parametrize(
        "chapters_a,chapters_b,should_be_similar",
        [
            (1, 1, True),
            (1, 2, False),
            (100, 100, True),
            (100, 110, True),
            (100, 115, True),
        ],
    )
    def test_chapters_tolerance(
        self, scorer, chapters_a, chapters_b, should_be_similar
    ):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=chapters_a,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=chapters_b,
        )

        score = scorer.score(title_a, title_b)

        if should_be_similar:
            assert score >= 85.0
        else:
            assert score < 95.0

    def test_zero_chapters_both(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=0,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=0,
        )

        score = scorer.score(title_a, title_b)

        assert score > 0.0

    def test_one_zero_one_nonzero_chapters(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=100,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=0,
        )

        score = scorer.score(title_a, title_b)

        assert score > 0.0

    def test_large_numbers(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=10000,
            volumes=1000,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=10100,
            volumes=1010,
        )

        score = scorer.score(title_a, title_b)

        assert score >= 85.0


class TestListFields:
    """Test genres, categories, authors overlap (10% weight)"""

    def test_complete_genre_overlap(self, scorer):
        genres = [TitleGenre.ACTION, TitleGenre.FANTASY, TitleGenre.HORROR]
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=genres,
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=genres,
        )

        score = scorer.score(title_a, title_b)

        assert score >= 95.0

    def test_partial_genre_overlap(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[TitleGenre.ACTION, TitleGenre.FANTASY, TitleGenre.HORROR],
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[TitleGenre.ACTION, TitleGenre.FANTASY],
        )

        score = scorer.score(title_a, title_b)

        # Overlap coefficient correctly returns 100% when all genres from smaller set match
        assert score == 100.0

    def test_no_genre_overlap(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[TitleGenre.ACTION],
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[TitleGenre.ROMANCE],
        )

        score = scorer.score(title_a, title_b)

        assert score < 95.0

    def test_empty_genres_both(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[],
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[],
        )

        score = scorer.score(title_a, title_b)

        assert score > 0.0

    def test_different_list_sizes(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[TitleGenre.ACTION],
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            genres=[
                TitleGenre.ACTION,
                TitleGenre.FANTASY,
                TitleGenre.HORROR,
                TitleGenre.MYSTERY,
                TitleGenre.PSYCHOLOGICAL,
            ],
        )

        score = scorer.score(title_a, title_b)

        assert score >= 85.0

    def test_authors_overlap(self, scorer):
        title_a = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            authors=["Kentaro Miura"],
        )
        title_b = TitleData(
            name_en="Test",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            authors=["Kentaro Miura", "Studio Gaga"],
        )

        score = scorer.score(title_a, title_b)

        assert score >= 85.0


class TestWeightNormalization:
    """Test that scores are properly normalized"""

    def test_score_never_exceeds_100(self, scorer, base_title):
        title_a = base_title.model_copy()
        title_b = base_title.model_copy()

        score = scorer.score(title_a, title_b)

        assert score <= 100.0

    def test_only_names_filled(self, scorer):
        title_a = TitleData(
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        assert 0.0 < score <= 100.0

    def test_minimal_common_fields(self, scorer):
        title_a = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )
        title_b = TitleData(
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
        )

        score = scorer.score(title_a, title_b)

        # Names are blocking field - without names, score should be 0.0
        assert score == 0.0


class TestRealWorldScenarios:
    """Test realistic matching scenarios"""

    def test_perfect_duplicate(self, scorer, base_title):
        title_a = base_title.model_copy()
        title_b = base_title.model_copy()

        score = scorer.score(title_a, title_b)

        assert score >= 95.0

    def test_clear_duplicate_different_sources(self, scorer):
        title_a = TitleData(
            name_ru="Берсерк",
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=374,
            volumes=41,
            released_at=datetime(1989, 8, 25),
            genres=[TitleGenre.ACTION, TitleGenre.FANTASY],
            authors=["Kentaro Miura"],
            rating=9.4,
            scored_by=150000,
        )
        title_b = TitleData(
            name_en="Berserk",
            description_en="Dark fantasy manga",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=370,
            volumes=41,
            released_at=datetime(1989, 8, 20),
            genres=[TitleGenre.ACTION, TitleGenre.FANTASY, TitleGenre.HORROR],
            authors=["Kentaro Miura"],
            rating=9.5,
            scored_by=120000,
        )

        score = scorer.score(title_a, title_b)

        assert 85.0 <= score < 100.0

    def test_borderline_case(self, scorer):
        title_a = TitleData(
            name_en="Berserk",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=374,
            released_at=datetime(1989, 8, 25),
        )
        title_b = TitleData(
            name_en="Berserk of Gluttony",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=50,
            released_at=datetime(2017, 10, 1),
        )

        score = scorer.score(title_a, title_b)

        assert 50.0 <= score < 85.0

    def test_clear_non_match(self, scorer):
        title_a = TitleData(
            name_en="Attack on Titan",
            type=TitleType.MANGA,
            status=TitleStatus.FINISHED,
            chapters=139,
            released_at=datetime(2009, 9, 9),
            genres=[TitleGenre.ACTION, TitleGenre.DRAMA],
            authors=["Hajime Isayama"],
        )
        title_b = TitleData(
            name_en="One Piece",
            type=TitleType.MANGA,
            status=TitleStatus.ONGOING,
            chapters=1100,
            released_at=datetime(1997, 7, 22),
            genres=[TitleGenre.ACTION, TitleGenre.ADVENTURE],
            authors=["Eiichiro Oda"],
        )

        score = scorer.score(title_a, title_b)

        assert score < 50.0

    def test_same_title_different_editions(self, scorer):
        title_a = TitleData(
            name_en="Fullmetal Alchemist",
            type=TitleType.MANGA,
            status=TitleStatus.FINISHED,
            chapters=116,
            volumes=27,
            released_at=datetime(2001, 7, 12),
            genres=[TitleGenre.ACTION, TitleGenre.ADVENTURE, TitleGenre.FANTASY],
            authors=["Hiromu Arakawa"],
        )
        title_b = TitleData(
            name_en="Fullmetal Alchemist",
            alt_names=["Hagane no Renkinjutsushi"],
            type=TitleType.MANGA,
            status=TitleStatus.FINISHED,
            chapters=116,
            volumes=27,
            released_at=datetime(2001, 7, 12),
            genres=[TitleGenre.ACTION, TitleGenre.FANTASY],
            authors=["Hiromu Arakawa"],
        )

        score = scorer.score(title_a, title_b)

        assert score >= 90.0
