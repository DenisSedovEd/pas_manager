import re
import secrets
import string


def generate_secure_password(length: int = 20) -> str:
    # alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    alphabet = string.ascii_letters + string.digits + "!#$%&()*+,-.:;<=>?@[]^_{|}~"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!#$%&()*+,-.:;<=>?@[]^_{|}~" for c in password)
        ):
            return password




def escape_md(text: str) -> str:
    """Надежное экранирование всех спецсимволов для MarkdownV2"""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)


print(generate_secure_password())

