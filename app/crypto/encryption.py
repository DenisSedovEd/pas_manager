import base64
import os

from core.config import settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.crypto.exception import InvalidTag


def to_base64_str(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def from_base64_str(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def generate_salt() -> bytes:
    return os.urandom(settings.app.salt_size)


def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=settings.app.key_length,
        salt=salt,
        iterations=settings.app.iterations,
        backend=default_backend(),
    )
    return kdf.derive(master_password.encode("utf-8"))


def encrypt_data(data: str, master_password: str) -> dict:
    salt = generate_salt()
    key = derive_key(master_password, salt)

    aesgcm = AESGCM(key)
    data_bytes = data.encode("utf-8")
    nonce = os.urandom(12)

    ciphertext_with_tag = aesgcm.encrypt(nonce, data_bytes, associated_data=None)

    return {
        "encrypted_data": to_base64_str(ciphertext_with_tag),
        "salt": to_base64_str(salt),
        "nonce": to_base64_str(nonce),
    }


def decrypt_data(
    encrypted_data: str,
    salt: str,
    nonce: str,
    master_password: str,
) -> str:
    ciphertext_with_tag_bytes = from_base64_str(encrypted_data)
    new_salt = from_base64_str(salt)
    new_nonce = from_base64_str(nonce)

    key = derive_key(master_password, new_salt)

    aesgcm = AESGCM(key)

    try:
        decrypted_bytes = aesgcm.decrypt(
            new_nonce, ciphertext_with_tag_bytes, associated_data=None
        )
        return decrypted_bytes.decode("utf-8")

    except InvalidTag:
        raise ValueError("Неверный мастер-пароль.")
