from pydantic import BaseModel, Field
from typing import Optional



class CategoryResponseSchema(BaseModel):
    """Платформа с количеством аккаунтов"""
    id: str
    name: str = Field(description="Category name")
    icon: Optional[str] = Field(description="Category icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
    order: int
    accounts_count: int = Field(description="Number of accounts")


class CategoryRequestSchema(BaseModel):
    """Для создания платформы"""
    name: str = Field(description="Category name")
    icon: str = Field(description="Category icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
