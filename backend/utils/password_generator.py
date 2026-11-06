import re
import secrets
import string

from backend.core.shared_config import PASSWORD_EXCLUDED_CHARS, PASSWORD_LENGTH, PASSWORD_SPECIAL_CHARS

_EXCLUDED = set(PASSWORD_EXCLUDED_CHARS)
_ALPHABET = "".join(
    c for c in string.ascii_letters + string.digits if c not in _EXCLUDED
) + PASSWORD_SPECIAL_CHARS


def generate_secure_password(length: int = PASSWORD_LENGTH) -> str:
    while True:
        password = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in PASSWORD_SPECIAL_CHARS for c in password)
        ):
            return password




def escape_md(text: str) -> str:
    """Надежное экранирование всех спецсимволов для MarkdownV2"""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)
