import re

def tag_remover(text: str | None) -> str | None:
    """
    Remove HTML tags, special characters, and specific hyperlinks from text.
    """
    if not text:
        return

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