import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config import settings
import base64

from app.crypto.exception import InvalidTag


def to_base64_str(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def from_base64_str(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def generate_salt() -> bytes:
    return os.urandom(settings.app.salt_size)


def derive_key(master_password: str, salt: bytes) -> bytes:
    password_bytes = master_password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=settings.app.key_length,
        salt=salt,
        iterations=settings.app.iterations,
        backend=default_backend(),
    )
    return kdf.derive(master_password.encode())


def encrypt_data(data: str, key: bytes, salt: bytes = None) -> dict:
    aesgcm = AESGCM(key)
    data_bytes = data.encode()

    nonce = os.urandom(12)

    ciphertext_with_tag = aesgcm.encrypt(nonce, data_bytes, associated_data=None)

    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    return {
        "encrypted_data": to_base64_str(ciphertext),
        "salt": to_base64_str(salt),
        "nonce": to_base64_str(nonce),
        "tag": to_base64_str(tag),
    }


def decode_and_decrypt(
    encrypted_data_str: str,
    salt_str: str,
    nonce_str: str,
    tag_str: str,
    master_password: str,
) -> str:
    encrypted_data = from_base64_str(encrypted_data_str)
    salt = from_base64_str(salt_str)
    nonce = from_base64_str(nonce_str)
    tag = from_base64_str(tag_str)

    key = derive_key(master_password, salt)

    aesgcm = AESGCM(key)
    ciphertext_with_tag = encrypted_data + tag

    try:
        decrypted_bytes = aesgcm.decrypt(
            nonce, ciphertext_with_tag, associated_data=None
        )
        return decrypted_bytes.decode()
    except InvalidTag:
        raise ValueError("Неверный мастер-пароль.")
