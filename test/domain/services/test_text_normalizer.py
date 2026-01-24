from src.domain.services.text_normalizer import TextNormalizer
import pytest


class TestTextNormalizer:
    """Test suite for TextNormalizer service."""

    class TestNormalize:
        """Tests for the normalize method."""

        def test_normalize_none(self):
            """Test that None returns empty string."""
            assert TextNormalizer.normalize(None) == ""

        def test_normalize_empty_string(self):
            """Test that empty string returns empty string."""
            assert TextNormalizer.normalize("") == ""

        def test_normalize_cyrillic(self):
            """Test Cyrillic text normalization."""
            assert TextNormalizer.normalize("Атака Титанов") == "ataka titanov"

        def test_normalize_japanese(self):
            """Test Japanese text normalization."""
            result = TextNormalizer.normalize("進撃の巨人")
            assert result == "in i nou en"

        def test_normalize_english_with_punctuation(self):
            """Test English text with special characters."""
            assert TextNormalizer.normalize("Attack on Titan!") == "attack on titan"

        def test_normalize_uppercase_to_lowercase(self):
            """Test uppercase conversion."""
            assert TextNormalizer.normalize("HELLO WORLD") == "hello world"

        def test_normalize_special_characters(self):
            """Test removal of special characters."""
            assert TextNormalizer.normalize("Test@#$%^&*()Text") == "testtext"

        def test_normalize_multiple_spaces(self):
            """Test multiple spaces are normalized to single space."""
            assert TextNormalizer.normalize("hello    world") == "hello world"

        def test_normalize_leading_trailing_spaces(self):
            """Test leading and trailing spaces are removed."""
            assert TextNormalizer.normalize("  hello world  ") == "hello world"

        def test_normalize_numbers_preserved(self):
            """Test that numbers are preserved."""
            assert TextNormalizer.normalize("Test 123 456") == "test 123 456"

        def test_normalize_accented_characters(self):
            """Test accented characters are converted to ASCII."""
            assert TextNormalizer.normalize("café résumé") == "cafe resume"

    class TestNormalizeMultiple:
        """Tests for the normalize_multiple method."""

        def test_normalize_multiple_empty_list(self):
            """Test empty list returns empty string."""
            assert TextNormalizer.normalize_multiple([]) == ""

        def test_normalize_multiple_all_none(self):
            """Test list of None values returns empty string."""
            assert TextNormalizer.normalize_multiple([None, None]) == ""

        def test_normalize_multiple_single_text(self):
            """Test single text normalization."""
            assert TextNormalizer.normalize_multiple(["Hello World"]) == "hello world"

        def test_normalize_multiple_deduplicate_true(self):
            """Test deduplication of words."""
            result = TextNormalizer.normalize_multiple(
                ["Hello World", "World Test"], deduplicate=True
            )
            assert result == "hello world test"

        def test_normalize_multiple_deduplicate_false(self):
            """Test without deduplication."""
            result = TextNormalizer.normalize_multiple(
                ["Hello World", "World Test"], deduplicate=False
            )
            assert result == "hello world world test"

        def test_normalize_multiple_min_word_length(self):
            """Test minimum word length filtering."""
            result = TextNormalizer.normalize_multiple(
                ["Hello to World"], min_word_length=4
            )
            assert result == "hello world"

        def test_normalize_multiple_min_word_length_custom(self):
            """Test custom minimum word length."""
            result = TextNormalizer.normalize_multiple(
                ["I am a developer"], min_word_length=5
            )
            assert result == "developer"

        def test_normalize_multiple_with_none_values(self):
            """Test list with None values mixed in."""
            result = TextNormalizer.normalize_multiple(
                ["Hello", None, "World"], deduplicate=True
            )
            assert result == "hello world"

        def test_normalize_multiple_with_empty_strings(self):
            """Test list with empty strings."""
            result = TextNormalizer.normalize_multiple(
                ["Hello", "", "World"], deduplicate=True
            )
            assert result == "hello world"

        def test_normalize_multiple_preserve_order_with_deduplication(self):
            """Test that order is preserved when deduplicating."""
            result = TextNormalizer.normalize_multiple(
                ["Apple Banana", "Cherry Apple"], deduplicate=True
            )
            assert result == "apple banana cherry"

        def test_normalize_multiple_all_words_too_short(self):
            """Test when all words are below minimum length."""
            result = TextNormalizer.normalize_multiple(
                ["to", "in", "on"], min_word_length=3
            )
            assert result == ""

        def test_normalize_multiple_complex_example(self):
            """Test complex scenario with multiple features."""
            result = TextNormalizer.normalize_multiple(
                ["Attack on Titan", "Атака Титанов", "進撃の巨人"],
                deduplicate=True,
                min_word_length=3,
            )
            assert "attack" in result
            assert "titan" in result
