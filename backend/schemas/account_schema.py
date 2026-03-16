from typing import Optional
from pydantic import BaseModel, Field


class AccountListItemSchema(BaseModel):
    """Для списка аккаунтов (без пароля)"""
    id: int
    label: str = Field(description="Account label/display name")
    login: str = Field(description="Username")
    order: int = Field(description="Account order")
    category_id: str = Field(description="Category ID")
    resource_id: str = Field(description="Resource ID")


class AccountDetailSchema(BaseModel):
    """Для детального просмотра аккаунта (с расшифровкой)"""
    id: int
    login: str = Field(description="Username")
    password: str = Field(description="Password")
    email: Optional[str] = Field(default=None, description="Email")
    phone: Optional[str] = Field(default=None, description="Phone")
    label: str = Field(description="Account label")
    category_id: str = Field(description="Category ID")
    resource_id: str = Field(description="Resource ID")



class AccountRequestSchema(BaseModel):
    """Для создания/обновления аккаунта"""
    category_id: str = Field(description="Category ID")
    resource_id: str = Field(description="Resource ID")
    login: str = Field(description="Username")
    password: str = Field(description="Password")
    email: Optional[str] = Field(default=None, description="Email")
    phone: Optional[str] = Field(default=None, description="Phone")
    label: Optional[str] = Field(default=None, description="Account label")
    order: Optional[int] = Field(default=0, description="Account order")
