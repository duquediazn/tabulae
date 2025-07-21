from app.models.user import User
import unicodedata


def is_admin_user(user: User) -> bool:
    """Returns True if the user is an admin, False otherwise."""
    return user.role.strip().lower() == "admin"


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


"""
unicodedata.normalize('NFD', category)

NFD stands for "Normalization Form Decomposition".
It splits accented characters into two parts:
- Base character (e.g., "e")
- Accent mark (e.g., "´")

Output: E l e c t r o ´ n i c a

unicodedata.category(c) != 'Mn'

unicodedata.category(c) returns the Unicode category of the character.
"Mn" means "Mark, Nonspacing" (accents, diacritics, etc.).
The condition filters out accent marks.

''.join(...)

Joins all filtered characters into a new string without accents.
"""
