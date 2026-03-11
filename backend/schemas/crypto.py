from typing import Optional

from pydantic import BaseModel


class EncryptedAccountSchema(BaseModel):
    id: Optional[int]
    service_name: str
    username: str
    encrypted_login: str
    encrypted_password: str

    salt: str
    nonce: str
    tag: str


class CryptoException(Exception):
    pass


class InvalidTag(CryptoException):
    pass


class EncodingToBytesError(CryptoException):
    pass