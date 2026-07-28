import re
import unicodedata


def normalize_search_text(value: str | None) -> str:

    if not value:
        return ""

    normalized = unicodedata.normalize("NFKD", value)

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    lowered = without_accents.casefold()

    cleaned = re.sub(r"\s+", " ", lowered)

    return cleaned.strip()