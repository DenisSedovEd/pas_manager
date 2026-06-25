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


class AccountSuggestionsSchema(BaseModel):
    login: list[str] = Field(
        default_factory=list,
        description="Logins from accounts",
    )
    email: list[str] = Field(
        default_factory=list,
        description="Emails from accounts",
    )
    phone: list[str] = Field(
        default_factory=list,
        description="Phones from accounts",
    )
    label: list[str] = Field(
        default_factory=list,
        description="Labels from accounts",
    )


class SearchResultItemSchema(BaseModel):
    """Элемент результата глобального поиска"""
    account_id: int
    login: str
    label: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    category_id: str
    category_name: str
    category_icon: Optional[str] = None
    parent_category_name: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
