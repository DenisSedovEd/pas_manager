from pydantic import BaseModel, Field
from typing import Optional



class PlatformResponseSchema(BaseModel):
    """Платформа с количеством аккаунтов"""
    id: str
    name: str = Field(description="Platform name")
    icon: Optional[str] = Field(description="Platform icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
    order: int
    accounts_count: int = Field(description="Number of accounts")


class PlatformRequestSchema(BaseModel):
    """Для создания платформы"""
    name: str = Field(description="Platform name")
    icon: str = Field(description="Platform icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
