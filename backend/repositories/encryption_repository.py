import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.schemas.crypto import EncodingToBytesError
from backend.core.config import settings


class EncryptionRepository:
    def to_base64_str(self, data: bytes) -> str | None:
        try:
            return base64.b64encode(data).decode("utf-8")
        except UnicodeDecodeError as e:
            raise EncodingToBytesError(f"Ошибка перевода в байты {e}")

    def from_base64_str(self, data: str) -> bytes | None:
        try:
            return base64.b64decode(data.encode("utf-8"))
        except UnicodeDecodeError as e:
            raise EncodingToBytesError(f"Ошибка перевода в байты {e}")

    def generate_salt(
        self,
    ) -> bytes:
        return os.urandom(settings.crypto.salt_size)

    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=settings.crypto.key_length,
            salt=salt,
            iterations=settings.crypto.iterations,
            backend=default_backend(),
        )
        return kdf.derive(master_password.encode("utf-8"))

    def encrypt_data(self, data: str, master_password: str) -> dict:
        salt = self.generate_salt()
        key = self.derive_key(master_password, salt)

        aesgcm = AESGCM(key)
        data_bytes = data.encode("utf-8")
        nonce = os.urandom(12)

        ciphertext = aesgcm.encrypt(nonce, data_bytes, associated_data=None)

        return {
            "encrypted_data": self.to_base64_str(ciphertext),
            "salt": self.to_base64_str(salt),
            "nonce": self.to_base64_str(nonce),
            "tag": '',
        }

    def decrypt_data(
        self,
        encrypted_data: str,
        salt: str,
        nonce: str,
        master_password: str,
    ) -> str:
        new_encrypted_data = self.from_base64_str(encrypted_data)
        new_salt = self.from_base64_str(salt)
        new_nonce = self.from_base64_str(nonce)

        key = self.derive_key(master_password, new_salt)

        aesgcm = AESGCM(key)

        decrypted_data = aesgcm.decrypt(
            new_nonce, new_encrypted_data, associated_data=None
        ).decode("utf-8")
        return decrypted_data
