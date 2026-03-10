from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from uuid import UUID


class PlatformSchema(BaseModel):
    id: UUID | str
    name: str = Field(alias="platform_name")
    icon: str = "🌐"
    accounts_count: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PlatformResponseSchema(BaseModel):
    """Платформа с количеством аккаунтов"""
    id: str  # ← Строка вместо UUID
    name: str = Field(description="Platform name")
    icon: str = Field(description="Platform icon/emoji")
    accounts_count: int = Field(description="Number of accounts")


class PlatformRequestSchema(BaseModel):
    """Для создания платформы"""
    name: str = Field(description="Platform name")
    icon: str = Field(description="Platform icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
