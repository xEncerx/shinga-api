import re


def tag_remover(text: str) -> str:
    """
    Remove HTML tags, special characters, and specific hyperlinks from text.
    This function cleans the input text by removing:
    - HTML tags (e.g., <div>, <p>, etc.)
    - HTML special characters (e.g., &nbsp;, &amp;, etc.)
    - Remanga-specific hyperlinks (e.g., [character=X], [/character])
    - Double quotes and consecutive newlines
    Args:
            text (str): The input text to be cleaned. If None, returns an empty string.
    Returns:
            str: The cleaned text with all specified elements removed and whitespace trimmed.
    """
    if text is None:
        return ""

    html_tag_regex = re.compile(r"<[^>]*>", re.MULTILINE | re.IGNORECASE)
    special_chars_regex = re.compile(r"&.*?;", re.MULTILINE | re.IGNORECASE)
    remanga_hyperlink_regex = re.compile(
        r"\[\/?character(=[^\]]+)?\]",
        re.MULTILINE | re.IGNORECASE,
    )

    cleaned_text = html_tag_regex.sub("", text)
    cleaned_text = special_chars_regex.sub("", cleaned_text)
    cleaned_text = remanga_hyperlink_regex.sub("", cleaned_text)
    cleaned_text = cleaned_text.strip()
    cleaned_text = cleaned_text.replace('"', "").replace("\n\n", "\n")

    return cleaned_text
