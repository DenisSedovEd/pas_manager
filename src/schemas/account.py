from typing import Optional
from pydantic import BaseModel, Field


class AccountListItemSchema(BaseModel):
    """Для списка аккаунтов (без пароля)"""
    id: int
    label: str = Field(description="Account label/display name")
    login: str = Field(description="Username")
    platform_id: str  # ← Строка вместо UUID


class AccountDetailSchema(BaseModel):
    """Для детального просмотра аккаунта (с расшифровкой)"""
    id: int
    login: str = Field(description="Username")
    password: str = Field(description="Password")
    email: Optional[str] = Field(default=None, description="Email")
    phone: Optional[str] = Field(default=None, description="Phone")
    label: str = Field(description="Account label")
    platform_id: str  # ← Строка вместо UUID


class AccountRequestSchema(BaseModel):
    """Для создания/обновления аккаунта"""
    platform_id: str = Field(description="Platform ID")  # ← Строка
    login: str = Field(description="Username")
    password: str = Field(description="Password")
    email: Optional[str] = Field(default=None, description="Email")
    phone: Optional[str] = Field(default=None, description="Phone")
    label: Optional[str] = Field(default=None, description="Account label")


class AccountResponseSchema(BaseModel):
    """Ответ при создании/обновлении"""
    status: str
    message: str
    data: Optional[AccountDetailSchema] = None