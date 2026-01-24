from unidecode import unidecode
import re


class TextNormalizer:
    """Service for normalizing text for search and matching purposes."""

    @staticmethod
    def normalize(text: str | None) -> str:
        """
        Normalize title to lowercase ASCII for search.

        Args:
            title: Title in any language

        Returns:
            Normalized title (lowercase, ASCII only, no special chars)

        Examples:
            `TextNormalizer.normalize("Атака Титанов")` -> "ataka titanov" \n
            `TextNormalizer.normalize("進撃の巨人")` -> "in i nou en" \n
            `TextNormalizer.normalize("Attack on Titan!")` -> "attack on titan" \n
        """
        if text is None:
            return ""

        text = unidecode(text.lower())
        text = re.sub(r"[^a-z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def normalize_multiple(
        texts: list[str | None],
        deduplicate: bool = True,
        min_word_length: int = 3,
    ) -> str:
        normalized_texts = []
        for text in texts:
            if text:
                normalized = TextNormalizer.normalize(text)
                if normalized:
                    normalized_texts.append(normalized)

        if not normalized_texts:
            return ""

        if not deduplicate:
            return " ".join(normalized_texts)

        seen_words = set()
        result_parts = []

        for normalized_text in normalized_texts:
            words = [
                word
                for word in normalized_text.split()
                if len(word) >= min_word_length and word not in seen_words
            ]

            if words:
                seen_words.update(words)
                result_parts.append(" ".join(words))

        return " ".join(result_parts)
