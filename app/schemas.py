from typing import Optional

from pydantic import BaseModel


class EditAccountSchema(BaseModel):
    service_name: str
    username: str | None
    password: str | None


class CreateAccountSchema(BaseModel):
    service_name: str
    username: str
    password: str


class ResponseAccountSchema(BaseModel):
    username: str
    password: str


class EncryptedAccountSchema(BaseModel):
    id: Optional[int]
    service_name: str
    username: str
    encrypted_login: str
    encrypted_password: str

    salt: str
    nonce: str
    tag: str
