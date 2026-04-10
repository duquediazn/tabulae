from app.models.user import User
import unicodedata


def normalize_category(category: str) -> str:
    """Normalizes the category name:
    - Removes accents
    - Capitalizes the first letter
    - Removes extra whitespace
    """
    category = category.strip()  # Remove surrounding spaces
    category = "".join(
        c
        for c in unicodedata.normalize("NFD", category)
        if unicodedata.category(c) != "Mn"
    )  # Remove accents
    return category.capitalize()